from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.session import Base

class AIHistory(Base):
    """
    SQLAlchemy model representing a record of AI content generation history.
    Tracks queries submitted to the LLM (like letters generation) and the response content.
    """
    __tablename__ = "ai_histories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    loan_id = Column(Integer, ForeignKey("loans.id", ondelete="SET NULL"), nullable=True)
    prompt_type = Column(String(100), nullable=False)
    prompt = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    timestamp = Column(DateTime, server_default=func.now(), nullable=False)

    # Audit Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    # Belongs to User
    user = relationship("User", back_populates="ai_histories")
    # Belongs to Loan
    loan = relationship("Loan", back_populates="ai_histories")
