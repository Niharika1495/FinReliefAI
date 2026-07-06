from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.session import Base

class FinancialProfile(Base):
    """
    SQLAlchemy model representing a User's Financial Profile.
    Maintains computed financial statistics like debt-to-income and monthly aggregates.
    """
    __tablename__ = "financial_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    emi_ratio = Column(Float, default=0.0, nullable=False)
    dti_ratio = Column(Float, default=0.0, nullable=False)
    monthly_surplus = Column(Float, default=0.0, nullable=False)
    stress_level = Column(String(50), nullable=True)

    # Audit Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    # Belongs to User
    user = relationship("User", back_populates="financial_profile")
