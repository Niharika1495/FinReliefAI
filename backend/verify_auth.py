import sys
import os
import warnings
from sqlalchemy.orm import Session
from fastapi import HTTPException

# Add parent directory to sys.path so we can import app modules directly
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

def verify():
    print("=== FinRelief AI Authentication & JWT Verification ===")

    # 1. Imports and Syntax Verification
    print("1. Verifying imports and dependencies...")
    try:
        from app.database.session import SessionLocal, engine, Base
        from app.models.user import User
        from app.models.financial_profile import FinancialProfile
        from app.schemas.auth import RegisterRequest, LoginRequest
        from app.services.auth_service import AuthService
        from app.auth.jwt import decode_token
        from app.dependencies.auth import get_current_user
        print("[OK] Imports resolve correctly. No circular imports.")
    except Exception as e:
        print(f"[ERROR] Import/Syntax verification failed: {str(e)}")
        sys.exit(1)

    # 2. Configure SQLAlchemy relationships mapping validation
    print("2. Verifying SQLAlchemy relationship configuration...")
    try:
        from sqlalchemy.orm import configure_mappers
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            configure_mappers()
            
            sql_warnings = [warning for warning in w if "sqlalchemy" in str(warning.category).lower()]
            if sql_warnings:
                print("[ERROR] SQLAlchemy Warnings detected:")
                for warning in sql_warnings:
                    print(f"  - {warning.message}")
                sys.exit(1)
            else:
                print("[OK] SQLAlchemy relationships compiled without warnings.")
    except Exception as e:
        print(f"[ERROR] SQLAlchemy relationship compilation failed: {str(e)}")
        sys.exit(1)

    # Initialize tables
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    # Test credentials constants
    TEST_EMAIL = "auth.test@finrelief.ai"
    TEST_PASSWORD = "super_secure_password_123"
    TEST_NAME = "Test Auth User"

    # Clean up any pre-existing test users using ORM-level delete to respect cascades
    user_to_cleanup = db.query(User).filter(User.email == TEST_EMAIL).first()
    if user_to_cleanup:
        db.delete(user_to_cleanup)
        db.commit()

    # 3. Register user verification
    print("3. Testing user registration...")
    try:
        register_payload = RegisterRequest(
            name=TEST_NAME,
            email=TEST_EMAIL,
            password=TEST_PASSWORD,
            monthly_income=5000.0,
            monthly_expenses=3000.0
        )
        
        user = AuthService.register_user(db=db, request=register_payload)
        
        # Assertions
        assert user.id is not None
        assert user.email == TEST_EMAIL
        assert user.name == TEST_NAME
        print("[OK] User registered successfully.")
    except Exception as e:
        print(f"[ERROR] User registration failed: {str(e)}")
        db.close()
        sys.exit(1)

    # 4. Hashed Password verification
    print("4. Testing password storage...")
    try:
        db.refresh(user)
        assert user.password != TEST_PASSWORD
        # bcrypt hashes start with $2a$ or $2b$
        assert user.password.startswith("$2")
        print("[OK] Passwords are encrypted and saved as bcrypt hashes. Plaintext is not stored.")
    except Exception as e:
        print(f"[ERROR] Password hashing verification failed: {str(e)}")
        db.close()
        sys.exit(1)

    # 5. Default Financial Profile creation
    print("5. Testing default FinancialProfile provisioning...")
    try:
        profile = db.query(FinancialProfile).filter(FinancialProfile.user_id == user.id).first()
        assert profile is not None
        assert profile.emi_ratio == 0.0
        assert profile.dti_ratio == 0.0
        assert profile.stress_level == "low"
        print("[OK] Default FinancialProfile created automatically upon user registration.")
    except Exception as e:
        print(f"[ERROR] Financial profile auto-creation failed: {str(e)}")
        db.close()
        sys.exit(1)

    # 6. Duplicate email rejection
    print("6. Testing duplicate email rejection...")
    try:
        AuthService.register_user(db=db, request=register_payload)
        print("[ERROR] Duplicate registration did not raise an exception.")
        db.close()
        sys.exit(1)
    except Exception as e:
        if hasattr(e, 'code') and e.code == "DUPLICATE_EMAIL":
            print("[OK] Duplicate email registration rejected successfully with status 400.")
        else:
            print(f"[ERROR] Unexpected exception on duplicate email: {str(e)}")
            db.close()
            sys.exit(1)

    # 7. Successful login & JWT generation
    print("7. Testing successful login credentials and JWT generation...")
    try:
        login_payload = LoginRequest(email=TEST_EMAIL, password=TEST_PASSWORD)
        login_result = AuthService.login_user(db=db, request=login_payload)
        
        assert "access_token" in login_result
        assert login_result["token_type"] == "bearer"
        assert login_result["user"].email == TEST_EMAIL
        
        token = login_result["access_token"]
        print(f"[OK] Authentication login succeeded. JWT generated successfully.")
    except Exception as e:
        print(f"[ERROR] Login authentication failed: {str(e)}")
        db.close()
        sys.exit(1)

    # 8. Wrong password rejection
    print("8. Testing wrong password credentials rejection...")
    try:
        wrong_login = LoginRequest(email=TEST_EMAIL, password="incorrect_password")
        AuthService.login_user(db=db, request=wrong_login)
        print("[ERROR] Login with incorrect credentials did not raise an exception.")
        db.close()
        sys.exit(1)
    except Exception as e:
        if hasattr(e, 'status_code') and e.status_code == 401:
            print("[OK] Wrong password login rejected successfully with status 401.")
        else:
            print(f"[ERROR] Unexpected exception on wrong password login: {str(e)}")
            db.close()
            sys.exit(1)

    # 9. Token parsing & get_current_user dependency validation
    print("9. Testing get_current_user dependency resolver...")
    try:
        import asyncio
        resolved_user = asyncio.run(get_current_user(token=token, db=db))
        assert resolved_user.id == user.id
        assert resolved_user.email == TEST_EMAIL
        print("[OK] get_current_user resolved user successfully using JWT claims.")
    except Exception as e:
        print(f"[ERROR] get_current_user dependency failed: {str(e)}")
        db.close()
        sys.exit(1)

    # 10. Invalid token rejection
    print("10. Testing invalid token credentials rejection...")
    try:
        import asyncio
        asyncio.run(get_current_user(token="invalid_token_header_payload_signature", db=db))
        print("[ERROR] Resolving invalid token did not raise an exception.")
        db.close()
        sys.exit(1)
    except HTTPException as http_err:
        if http_err.status_code == 401:
            print("[OK] Invalid token rejected successfully with status 401.")
        else:
            print(f"[ERROR] Unexpected status code on invalid token check: {http_err.status_code}")
            db.close()
            sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Unexpected exception type on invalid token check: {str(e)}")
        db.close()
        sys.exit(1)

    db.close()
    print("\n=== All Authentication System Checks Succeeded (10/10) ===")

if __name__ == "__main__":
    verify()
