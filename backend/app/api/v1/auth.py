from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService
from app.models.user import User

auth_router = APIRouter()

@auth_router.post(
    "/register", 
    response_model=UserResponse, 
    status_code=status.HTTP_201_CREATED, 
    summary="Register New User"
)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Registers a new user account and provisions their default financial profile.
    """
    return AuthService.register_user(db=db, request=request)

@auth_router.post(
    "/login", 
    response_model=TokenResponse, 
    summary="User Login Authentication"
)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Verifies user credentials and issues a JWT authorization access token.
    """
    return AuthService.login_user(db=db, request=request)

@auth_router.get(
    "/me", 
    response_model=UserResponse, 
    summary="Get Authenticated User Session"
)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Retrieves and returns the currently logged-in user profile.
    """
    return current_user
