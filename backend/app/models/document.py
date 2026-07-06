from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.session import Base

class DocumentMetadata(Base):
    """
    SQLAlchemy model representing uploaded documents and their extracted metadata details.
    """
    __tablename__ = "documents_metadata"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(50), nullable=False)
    
    # OCR Extracted details
    extracted_lender = Column(String(100), nullable=True)
    extracted_amount = Column(Float, nullable=True)
    extracted_emi = Column(Float, nullable=True)
    extracted_interest_rate = Column(Float, nullable=True)
    extracted_due_date = Column(String(50), nullable=True)
    extracted_loan_type = Column(String(50), nullable=True)
    
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="documents")
