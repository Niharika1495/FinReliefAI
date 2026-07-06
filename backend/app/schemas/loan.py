from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime
from app.models.loan import LoanStatus

class LoanBase(BaseModel):
    """
    Base properties shared between loan request and response schemas.
    """
    lender_name: str = Field(..., min_length=1, max_length=100, description="Name of the creditor / lender institution")
    loan_type: str = Field(..., min_length=1, max_length=50, description="Type of debt (e.g. personal, credit_card, auto)")
    outstanding_amount: float = Field(..., gt=0.0, description="Remaining principal amount balance")
    interest_rate: float = Field(..., ge=0.0, le=100.0, description="Annual interest rate percentage")
    emi: float = Field(..., ge=0.0, description="Monthly Equated Monthly Installment payment")
    overdue_months: int = Field(default=0, ge=0, description="Count of missed payments / months overdue")

class LoanCreate(LoanBase):
    """
    Schema for creating a new Loan. Includes only client-writable fields.
    """
    pass

class LoanUpdate(BaseModel):
    """
    Schema for updating an existing Loan. All fields are optional and validated.
    """
    lender_name: Optional[str] = Field(None, min_length=1, max_length=100)
    loan_type: Optional[str] = Field(None, min_length=1, max_length=50)
    outstanding_amount: Optional[float] = Field(None, gt=0.0)
    interest_rate: Optional[float] = Field(None, ge=0.0, le=100.0)
    emi: Optional[float] = Field(None, ge=0.0)
    overdue_months: Optional[int] = Field(None, ge=0)
    loan_status: Optional[LoanStatus] = Field(None)

class LoanResponse(LoanBase):
    """
    Schema for reading Loan details. Includes DB IDs, user ID, status, and audit timestamps.
    """
    id: int
    user_id: int
    is_active: bool
    loan_status: LoanStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
