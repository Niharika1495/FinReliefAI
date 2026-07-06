from sqlalchemy.orm import Session
from typing import List, Dict, Any
import logging
from app.models.notification import Notification
from app.models.user import User
from app.utils.exceptions import FinReliefException

logger = logging.getLogger("finrelief_ai")

class NotificationService:
    """
    Service layer implementing user alerts, database logging,
    and mock channel delivery (Email, SMS, WhatsApp).
    """

    @staticmethod
    def create_notification(
        db: Session,
        user_id: int,
        title: str,
        message: str,
        type: str = "ALERT"
    ) -> Notification:
        """
        Creates and logs a database alert. Dispatches mock external channel delivery.
        """
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=type
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)

        # Mock dispatch delivery
        NotificationService.dispatch_mock_channels(user_id, title, message)

        return notification

    @staticmethod
    def dispatch_mock_channels(user_id: int, title: str, message: str):
        """
        Simulates dispatching notifications to SMTP servers, SMS endpoints, and WhatsApp.
        """
        logger.info(f"[SMTP SEND MOCK] Sending email to User {user_id} - Title: {title} | Body: {message}")
        logger.info(f"[SMS SEND MOCK] Sending text to User {user_id} - MSG: {message[:50]}...")
        logger.info(f"[WHATSAPP SEND MOCK] Sending WhatsApp ping to User {user_id} - MSG: {title}: {message[:40]}")

    @staticmethod
    def get_notifications(db: Session, user: User, unread_only: bool = False) -> List[Notification]:
        """
        Queries all logged alerts for the user.
        """
        query = db.query(Notification).filter(Notification.user_id == user.id)
        if unread_only:
            query = query.filter(Notification.is_read == False)
        return query.order_by(Notification.created_at.desc()).all()

    @staticmethod
    def mark_as_read(db: Session, notification_id: int, user: User) -> Notification:
        """
        Marks an individual notification read. Validates tenant owner locks.
        """
        notification = db.query(Notification).filter(Notification.id == notification_id).first()
        if not notification:
            raise FinReliefException(
                status_code=404,
                error_code="NOTIFICATION_NOT_FOUND",
                message="Notification record not found."
            )
        if notification.user_id != user.id:
            raise FinReliefException(
                status_code=403,
                error_code="FORBIDDEN",
                message="You do not have permission to modify this notification."
            )
            
        notification.is_read = True
        db.commit()
        db.refresh(notification)
        return notification
