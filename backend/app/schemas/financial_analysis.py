from pydantic import BaseModel, Field, ConfigDict
from typing import List

class FinancialAnalysisResponse(BaseModel):
    """
    Standardized response schema detailing complete rule-based metrics,
    risk analysis tiers, and recommendations for a User's financial state.
    """
    financial_health_score: float = Field(..., ge=0.0, le=100.0, description="Calculated financial health score from 0 to 100")
    risk_level: str = Field(..., description="Determined risk level: LOW, MEDIUM, HIGH, CRITICAL")
    repayment_capacity: str = Field(..., description="Determined capacity: GOOD, MODERATE, WEAK, VERY_WEAK")
    monthly_income: float = Field(..., ge=0.0, description="User monthly income")
    monthly_expenses: float = Field(..., ge=0.0, description="User monthly expenses")
    monthly_surplus: float = Field(..., description="Remaining cash flow after monthly expenses and EMI obligations")
    total_active_loans: int = Field(..., ge=0, description="Number of non-soft-deleted active loan lines")
    total_outstanding: float = Field(..., ge=0.0, description="Total outstanding debt balance of active loans")
    total_monthly_emi: float = Field(..., ge=0.0, description="Aggregate monthly EMIs paid on active loans")
    dti_ratio: float = Field(..., ge=0.0, description="Debt-to-income percentage ratio")
    emi_ratio: float = Field(..., ge=0.0, description="EMI-to-income percentage ratio")
    average_interest_rate: float = Field(..., ge=0.0, description="Average annual interest rate of active loans")
    highest_interest_rate: float = Field(..., ge=0.0, description="Highest annual interest rate of active loans")
    maximum_overdue_months: int = Field(..., ge=0, description="Maximum overdue month count across active loans")
    recommendations: List[str] = Field(..., description="Generated action items from rule checks")

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "financial_health_score": 82.5,
                "risk_level": "LOW",
                "repayment_capacity": "GOOD",
                "monthly_income": 5000.0,
                "monthly_expenses": 2000.0,
                "monthly_surplus": 2500.0,
                "total_active_loans": 2,
                "total_outstanding": 15000.0,
                "total_monthly_emi": 500.0,
                "dti_ratio": 10.0,
                "emi_ratio": 10.0,
                "average_interest_rate": 7.5,
                "highest_interest_rate": 9.0,
                "maximum_overdue_months": 0,
                "recommendations": [
                    "Reduce discretionary spending to lower your debt-to-income ratio.",
                    "Save emergency funds."
                ]
            }
        }
    )
