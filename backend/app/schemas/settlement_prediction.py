from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime

class SettlementPredictionBase(BaseModel):
    """
    Base properties shared between settlement prediction request and response schemas.
    """
    loan_id: int = Field(..., description="Foreign key referencing the associated Loan")
    suggested_settlement: float = Field(..., ge=0.0, description="Suggested settlement offer amount")
    risk_category: str = Field(..., max_length=50, description="Prediction confidence risk category level")
    predicted_amount: float = Field(..., ge=0.0, description="Forecasted savings or prediction amount payoff value")

class SettlementPredictionCreate(SettlementPredictionBase):
    """
    Schema for creating a SettlementPrediction.
    """
    pass

class SettlementPredictionUpdate(BaseModel):
    """
    Schema for updating an existing SettlementPrediction. All fields are optional.
    """
    suggested_settlement: Optional[float] = Field(None, ge=0.0)
    risk_category: Optional[str] = Field(None, max_length=50)
    predicted_amount: Optional[float] = Field(None, ge=0.0)

class SettlementPredictionResponse(SettlementPredictionBase):
    """
    Schema for reading SettlementPrediction details. Includes DB IDs and audit timestamps.
    """
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
