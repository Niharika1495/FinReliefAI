from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime

class FinancialProfileBase(BaseModel):
    """
    Base properties shared across financial profile schema models.
    """
    emi_ratio: float = Field(default=0.0, ge=0.0, description="Aggregate EMI-to-income percentage ratio")
    dti_ratio: float = Field(default=0.0, ge=0.0, description="Aggregate Debt-to-income percentage ratio")
    monthly_surplus: float = Field(default=0.0, description="Remaining cash surplus after expenses and payments")
    stress_level: Optional[str] = Field(None, max_length=50, description="Calculated stress tier level indicator")

class FinancialProfileCreate(FinancialProfileBase):
    """
    Schema for creating a FinancialProfile.
    """
    user_id: int

class FinancialProfileUpdate(BaseModel):
    """
    Schema for updating an existing FinancialProfile and parent User details.
    All fields are optional and validated.
    """
    monthly_income: Optional[float] = Field(None, ge=0.0, description="Updated monthly income (stored on User model)")
    monthly_expenses: Optional[float] = Field(None, ge=0.0, description="Updated monthly expenses (stored on User model)")
    stress_level: Optional[str] = Field(None, max_length=50, description="Updated stress level tier")

class FinancialProfileResponse(FinancialProfileBase):
    """
    Flattened schema combining the database attributes from both the
    FinancialProfile and parent User models.
    """
    id: int
    user_id: int
    monthly_income: float
    monthly_expenses: float
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
