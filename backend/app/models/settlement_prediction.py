from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.session import Base

class SettlementPrediction(Base):
    """
    SQLAlchemy model representing a predicted debt settlement option for a Loan.
    Stores the suggested settlement offer, risk metrics, and forecasted payoff amounts.
    """
    __tablename__ = "settlement_predictions"

    id = Column(Integer, primary_key=True, index=True)
    loan_id = Column(Integer, ForeignKey("loans.id", ondelete="CASCADE"), nullable=False)
    suggested_settlement = Column(Float, nullable=False)
    risk_category = Column(String(50), nullable=False)
    predicted_amount = Column(Float, nullable=False)

    # Audit Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    # Belongs to Loan
    loan = relationship("Loan", back_populates="settlement_predictions")
