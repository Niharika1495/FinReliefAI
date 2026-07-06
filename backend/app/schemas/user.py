from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    """
    Base properties shared between user request and response schemas.
    """
    name: str = Field(..., max_length=100, description="Full name of the user")
    email: str = Field(..., max_length=255, description="Unique email address")
    monthly_income: float = Field(default=0.0, ge=0.0, description="Monthly income in USD")
    monthly_expenses: float = Field(default=0.0, ge=0.0, description="Monthly expenses in USD")

class UserCreate(UserBase):
    """
    Schema for creating a new User. Includes the raw password.
    """
    password: str = Field(..., min_length=6, max_length=255, description="Plaintext password")

class UserUpdate(BaseModel):
    """
    Schema for updating an existing User's details. All fields are optional.
    """
    name: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, max_length=255)
    password: Optional[str] = Field(None, min_length=6, max_length=255)
    monthly_income: Optional[float] = Field(None, ge=0.0)
    monthly_expenses: Optional[float] = Field(None, ge=0.0)

class UserResponse(UserBase):
    """
    Schema for reading User details. Includes DB IDs and audit timestamps.
    """
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
