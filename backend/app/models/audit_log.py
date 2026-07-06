from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database.session import Base

class AuditLog(Base):
    """
    SQLAlchemy model representing system audit logging logs.
    Captures mutations, auth states, and administrative queries.
    """
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True, index=True)
    timestamp = Column(DateTime, server_default=func.now(), nullable=False)
    action = Column(String(255), nullable=False)
    ip_address = Column(String(50), nullable=True)
    endpoint = Column(String(255), nullable=True)
    request_id = Column(String(100), nullable=True)
