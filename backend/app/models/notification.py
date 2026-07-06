from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.session import Base

class Notification(Base):
    """
    SQLAlchemy model representing alerts and reminders created for a User.
    """
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(100), nullable=False)
    message = Column(String(500), nullable=False)
    type = Column(String(50), nullable=False)  # REMINDER, SUMMARY, ALERT
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="notifications")
