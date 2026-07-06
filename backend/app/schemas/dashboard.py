from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Optional, Any
from datetime import datetime

class DashboardOverviewResponse(BaseModel):
    """
    Schema representing user dashboard overview aggregates.
    """
    user_name: str
    financial_health_score: float
    risk_level: str
    repayment_capacity: str
    monthly_income: float
    monthly_expenses: float
    monthly_surplus: float
    total_active_loans: int
    total_outstanding_amount: float
    total_monthly_emi: float
    eligible_settlements: int
    estimated_savings: float
    highest_priority_loan: Optional[str] = None
    recent_ai_activity_count: int

    model_config = ConfigDict(from_attributes=True)

class FinancialSummaryResponse(BaseModel):
    """
    Schema representing aggregate financial summary metrics.
    """
    income: float
    expenses: float
    emi: float
    surplus: float
    dti: float
    emi_ratio: float
    financial_score: float
    risk: str

    model_config = ConfigDict(from_attributes=True)

class LoanAnalyticsResponse(BaseModel):
    """
    Schema representing specific analytics over user's liability assets.
    """
    loan_count: int
    outstanding_amount: float
    average_interest_rate: float
    highest_interest_rate: float
    loan_type_distribution: Dict[str, int]
    loan_status_distribution: Dict[str, int]
    outstanding_amount_by_lender: Dict[str, float]
    highest_priority_loan: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class SettlementAnalyticsResponse(BaseModel):
    """
    Schema representing detailed metrics over target debt settlements.
    """
    eligible_loans: int
    partially_eligible_loans: int
    not_eligible_loans: int
    average_settlement_percentage: float
    total_estimated_savings: float
    total_recommended_settlement: float
    negotiation_difficulty_distribution: Dict[str, int]

    model_config = ConfigDict(from_attributes=True)

class AIActivityItem(BaseModel):
    """
    Nested model for listing recent AI log requests.
    """
    id: int
    loan_id: Optional[int] = None
    prompt_type: str
    prompt: str
    response: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class AIAnalyticsResponse(BaseModel):
    """
    Schema representing details on AI letter generations and queries history.
    """
    total_ai_requests: int
    negotiation_strategies_generated: int
    settlement_letters_generated: int
    negotiation_emails_generated: int
    financial_explanations_generated: int
    recent_ai_activities: List[AIActivityItem]

    model_config = ConfigDict(from_attributes=True)

class ChartItem(BaseModel):
    """
    Universal key-value structure for charts data.
    """
    name: str
    value: float

class LenderAmountItem(BaseModel):
    """
    Lender to outstanding amount mapping.
    """
    lender_name: str
    outstanding_amount: float

class LenderRateItem(BaseModel):
    """
    Lender to interest rate mapping.
    """
    lender_name: str
    interest_rate: float

class ChartDataResponse(BaseModel):
    """
    Schema representing structured lists ready to bind to frontend visualization libraries.
    """
    loan_type_pie_chart: List[ChartItem]
    loan_status_pie_chart: List[ChartItem]
    interest_rate_bar_chart: List[LenderRateItem]
    outstanding_amount_by_lender: List[LenderAmountItem]
    settlement_eligibility_chart: List[ChartItem]
    financial_score_gauge_value: float

    model_config = ConfigDict(from_attributes=True)
