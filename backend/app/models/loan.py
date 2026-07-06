import enum
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.session import Base

class LoanStatus(str, enum.Enum):
    """
    Python Enum representing the status of a loan.
    """
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"
    SETTLED = "SETTLED"
    DEFAULTED = "DEFAULTED"

class Loan(Base):
    """
    SQLAlchemy model representing a User's Loan / Liability account.
    Tracks lender name, outstanding balance, monthly EMI, and overdue status.
    Now supports soft delete tracking and status enums.
    """
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    lender_name = Column(String(100), nullable=False)
    loan_type = Column(String(50), nullable=False)
    outstanding_amount = Column(Float, nullable=False)
    interest_rate = Column(Float, nullable=False)
    emi = Column(Float, nullable=False)
    overdue_months = Column(Integer, default=0, nullable=False)

    # Soft Delete & Status
    is_active = Column(Boolean, default=True, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    loan_status = Column(SQLEnum(LoanStatus), default=LoanStatus.ACTIVE, nullable=False)

    # Audit Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    # Belongs to User
    user = relationship("User", back_populates="loans")
    
    # Has many SettlementPrediction records
    settlement_predictions = relationship(
        "SettlementPrediction",
        back_populates="loan",
        cascade="all, delete-orphan"
    )

    # Has many SettlementRecommendation records
    settlement_recommendations = relationship(
        "SettlementRecommendation",
        back_populates="loan",
        cascade="all, delete-orphan"
    )

    # Has many AIHistory records
    ai_histories = relationship(
        "AIHistory",
        back_populates="loan",
        cascade="all, delete-orphan"
    )
