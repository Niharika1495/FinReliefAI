from sqlalchemy.orm import Session
from typing import Optional
from app.models.audit_log import AuditLog

class AuditService:
    """
    Service layer for administrative audit logging of user and admin interactions.
    """

    @staticmethod
    def create_log(
        db: Session,
        user_id: Optional[int],
        action: str,
        ip_address: Optional[str] = None,
        endpoint: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> AuditLog:
        """
        Creates and persists an audit log entry in the database.
        """
        log = AuditLog(
            user_id=user_id,
            action=action,
            ip_address=ip_address,
            endpoint=endpoint,
            request_id=request_id
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log
