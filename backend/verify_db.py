import os
import sys
import warnings

def verify():
    print("=== FinRelief AI Database Schema Verification ===")
    
    # 1. Check syntax and imports
    print("1. Checking syntax and importing models & schemas...")
    try:
        from app.database.session import Base, engine
        from app.models.user import User
        from app.models.financial_profile import FinancialProfile
        from app.models.loan import Loan
        from app.models.settlement_prediction import SettlementPrediction
        from app.models.ai_history import AIHistory
        
        from app.schemas.user import UserResponse
        from app.schemas.financial_profile import FinancialProfileResponse
        from app.schemas.loan import LoanResponse
        from app.schemas.settlement_prediction import SettlementPredictionResponse
        from app.schemas.ai_history import AIHistoryResponse
        
        print("[OK] All models and schemas imported successfully without syntax errors or circular imports.")
    except Exception as e:
        print(f"[ERROR] Import/Syntax error: {str(e)}")
        sys.exit(1)
        
    # 2. Check SQLAlchemy warnings and compile relationships
    print("2. Checking SQLAlchemy relationship compilation...")
    try:
        # Trigger compilation of all mapper mappings and relationships
        from sqlalchemy.orm import configure_mappers
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            configure_mappers()
            
            # Check for SQLAlchemy warnings
            sql_warnings = [warning for warning in w if "sqlalchemy" in str(warning.category).lower()]
            if sql_warnings:
                print("[ERROR] SQLAlchemy Warnings detected during mapper configuration:")
                for warning in sql_warnings:
                    print(f"  - {warning.message}")
                sys.exit(1)
            else:
                print("[OK] Relationships compiled successfully without any warnings.")
    except Exception as e:
        print(f"[ERROR] Relationship compilation error: {str(e)}")
        sys.exit(1)

    # 3. Create tables in SQLite (to verify table creation and database file existence)
    print("3. Initializing database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("[OK] Database tables created successfully.")
    except Exception as e:
        print(f"[ERROR] Table creation failed: {str(e)}")
        sys.exit(1)

    # 4. Check if finrelief.db exists
    print("4. Checking database file existence...")
    db_path = "finrelief.db"
    
    if os.path.exists(db_path):
        print(f"[OK] Database file exists at: {os.path.abspath(db_path)}")
    else:
        print("[ERROR] Database file 'finrelief.db' could not be found.")
        sys.exit(1)

    # 5. Check if all five tables exist
    print("5. Verifying table metadata in SQLite database...")
    try:
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        expected_tables = ["users", "financial_profiles", "loans", "settlement_predictions", "ai_histories"]
        missing_tables = [t for t in expected_tables if t not in tables]
        
        if missing_tables:
            print(f"[ERROR] Missing tables: {missing_tables}")
            sys.exit(1)
        else:
            print(f"[OK] All five tables exist: {tables}")
    except Exception as e:
        print(f"[ERROR] Table verification failed: {str(e)}")
        sys.exit(1)

    print("\n=== Verification Successful: Database foundation & ORM compile clean ===")

if __name__ == "__main__":
    verify()
