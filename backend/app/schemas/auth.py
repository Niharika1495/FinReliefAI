from pydantic import BaseModel, Field
from typing import Optional
from app.schemas.user import UserResponse

class RegisterRequest(BaseModel):
    """
    Schema representing user registration payload.
    Includes basic string lengths and financial bounds validations.
    """
    name: str = Field(..., min_length=1, max_length=100, description="Full name of the user")
    email: str = Field(..., min_length=3, max_length=255, description="Unique email address")
    password: str = Field(..., min_length=6, max_length=255, description="Password (min 6 characters)")
    monthly_income: Optional[float] = Field(default=0.0, ge=0.0, description="Monthly income in USD")
    monthly_expenses: Optional[float] = Field(default=0.0, ge=0.0, description="Monthly expenses in USD")

class LoginRequest(BaseModel):
    """
    Schema representing user login credentials payload.
    """
    email: str = Field(..., min_length=3, max_length=255, description="Registered email address")
    password: str = Field(..., min_length=6, max_length=255, description="User password")

class TokenResponse(BaseModel):
    """
    Schema representing the successful login token response containing JWT access details.
    """
    access_token: str
    token_type: str
    user: UserResponse
