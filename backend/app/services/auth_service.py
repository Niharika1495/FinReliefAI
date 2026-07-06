from sqlalchemy.orm import Session
from app.models.user import User
from app.models.financial_profile import FinancialProfile
from app.schemas.auth import RegisterRequest, LoginRequest
from app.auth.password import hash_password, verify_password
from app.auth.jwt import create_access_token
from app.utils.exceptions import FinReliefException

class AuthService:
    """
    Service class handling user registration, authentication verification,
    and access token generation. Decoupled from HTTP routing logic.
    """

    @staticmethod
    def register_user(db: Session, request: RegisterRequest) -> User:
        """
        Registers a new User, validates email uniqueness, hashes passwords,
        and initializes a default FinancialProfile entity.
        """
        # Validate that email is not already registered
        existing_user = db.query(User).filter(User.email == request.email).first()
        if existing_user:
            raise FinReliefException(
                message="Email address is already registered.",
                code="DUPLICATE_EMAIL",
                status_code=400
            )

        # Hash plaintext password
        hashed_password = hash_password(request.password)

        # Create user record
        new_user = User(
            name=request.name,
            email=request.email,
            password=hashed_password,
            monthly_income=request.monthly_income,
            monthly_expenses=request.monthly_expenses
        )
        
        db.add(new_user)
        db.flush()  # Retrieve new_user.id for FK mappings

        # Initialize default Financial Profile linked to the User
        default_profile = FinancialProfile(
            user_id=new_user.id,
            emi_ratio=0.0,
            dti_ratio=0.0,
            monthly_surplus=request.monthly_income - request.monthly_expenses,
            stress_level="low"
        )
        db.add(default_profile)
        
        try:
            db.commit()
            db.refresh(new_user)
            return new_user
        except Exception as e:
            db.rollback()
            raise FinReliefException(
                message=f"Registration transaction failed: {str(e)}",
                code="REGISTRATION_FAILED",
                status_code=500
            )

    @staticmethod
    def login_user(db: Session, request: LoginRequest) -> dict:
        """
        Authenticates user credentials and returns a signed access token.
        Tracks failed login attempts and locks out the account after 5 failures.
        """
        from datetime import datetime, timedelta

        user = db.query(User).filter(User.email == request.email).first()
        if not user:
            raise FinReliefException(
                message="Invalid email or password.",
                code="INVALID_CREDENTIALS",
                status_code=401
            )

        # Check for lockout status
        if user.lockout_until and user.lockout_until > datetime.now():
            minutes_left = int((user.lockout_until - datetime.now()).total_seconds() / 60) + 1
            raise FinReliefException(
                message=f"Account is temporarily locked. Please try again in {minutes_left} minute(s).",
                code="ACCOUNT_LOCKED",
                status_code=403
            )

        # Verify hashed password
        if not verify_password(request.password, user.password):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                user.lockout_until = datetime.now() + timedelta(minutes=15)
                db.commit()
                raise FinReliefException(
                    message="Invalid email or password. Account is now locked for 15 minutes.",
                    code="ACCOUNT_LOCKED",
                    status_code=403
                )
            db.commit()
            raise FinReliefException(
                message="Invalid email or password.",
                code="INVALID_CREDENTIALS",
                status_code=401
            )

        # Reset failed attempts on success
        user.failed_login_attempts = 0
        user.lockout_until = None
        db.commit()

        # Construct payload with email as subject and generate token
        token_payload = {"sub": user.email}
        token = create_access_token(data=token_payload)

        return {
            "access_token": token,
            "token_type": "bearer",
            "user": user
        }
