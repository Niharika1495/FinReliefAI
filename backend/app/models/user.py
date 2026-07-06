from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.session import Base

class User(Base):
    """
    SQLAlchemy model representing a registered User in the platform.
    Defines core fields, audit timestamps, and one-to-many / one-to-one relations.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    monthly_income = Column(Float, default=0.0, nullable=False)
    monthly_expenses = Column(Float, default=0.0, nullable=False)

    # Security Hardening & Accounts Verification
    is_verified = Column(Integer, default=0, nullable=False)
    verification_token = Column(String(255), nullable=True)
    reset_token = Column(String(255), nullable=True)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    lockout_until = Column(DateTime, nullable=True)
    refresh_token = Column(String(255), nullable=True)

    # Audit Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    # One User -> One FinancialProfile
    financial_profile = relationship(
        "FinancialProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    
    # One User -> Many Loans
    loans = relationship(
        "Loan",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    # One User -> Many SettlementRecommendations
    settlement_recommendations = relationship(
        "SettlementRecommendation",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    # One User -> Many AIHistory records
    ai_histories = relationship(
        "AIHistory",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # One User -> Many Notifications
    notifications = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    # One User -> Many DocumentMetadata
    documents = relationship(
        "DocumentMetadata",
        back_populates="user",
        cascade="all, delete-orphan"
    )
