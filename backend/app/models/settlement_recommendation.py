from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.session import Base

class SettlementRecommendation(Base):
    """
    SQLAlchemy model representing computed rule-based settlement recommendations for User loans.
    Tracks eligibility levels, target settlement amounts, and priority indicators.
    """
    __tablename__ = "settlement_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    loan_id = Column(Integer, ForeignKey("loans.id", ondelete="CASCADE"), nullable=False, index=True)
    eligibility = Column(String(50), nullable=False)
    settlement_percentage = Column(Float, nullable=False)
    recommended_amount = Column(Float, nullable=False)
    estimated_savings = Column(Float, nullable=False)
    estimated_payoff_months = Column(Integer, nullable=False)
    priority_score = Column(Float, nullable=False)
    negotiation_difficulty = Column(String(50), nullable=False)

    # Audit Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="settlement_recommendations")
    loan = relationship("Loan", back_populates="settlement_recommendations")
