from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime

class SettlementRecommendationResponse(BaseModel):
    """
    Schema representing computed individual loan settlement recommendation details.
    """
    id: int
    user_id: int
    loan_id: int
    eligibility: str = Field(..., description="Calculated eligibility: ELIGIBLE, PARTIALLY_ELIGIBLE, NOT_ELIGIBLE")
    settlement_percentage: float = Field(..., description="Target percentage of outstanding balance to offer for settlement")
    recommended_amount: float = Field(..., description="Target cash settlement amount to offer")
    estimated_savings: float = Field(..., description="Forecasted savings relative to outstanding balance")
    estimated_payoff_months: int = Field(..., description="Estimated payoff timeframe in integer months")
    priority_score: float = Field(..., description="Calculated priority ranking score between 0 and 100")
    negotiation_difficulty: str = Field(..., description="Estimated difficulty level: LOW, MEDIUM, HIGH, VERY_HIGH")
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SettlementSummaryResponse(BaseModel):
    """
    Schema summarizing active settlement targets, aggregates, and tips.
    """
    eligible_loans: int = Field(..., description="Count of loans marked ELIGIBLE or PARTIALLY_ELIGIBLE")
    average_settlement_percentage: float = Field(..., description="Average recommended settlement percentage across eligible lines")
    total_savings: float = Field(..., description="Sum of expected savings if settled")
    total_recommended_settlement: float = Field(..., description="Sum of recommended settlement target amounts")
    highest_priority_loan_id: Optional[int] = Field(None, description="ID of the loan with the highest priority score")
    highest_priority_loan_lender: Optional[str] = Field(None, description="Lender name of the highest priority loan")
    recommendations: List[str] = Field(..., description="Actionable payoff priorities list")

    model_config = ConfigDict(from_attributes=True)
