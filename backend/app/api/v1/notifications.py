from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.notification import NotificationResponse
from app.services.notification_service import NotificationService
from app.utils.response_utils import success_response

notifications_router = APIRouter()

@notifications_router.get(
    "",
    summary="List User Notifications"
)
def get_notifications(
    unread_only: bool = Query(False, description="Filter for unread notifications only"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves all notifications for the authenticated user (optionally filtered by unread status).
    """
    notifications = NotificationService.get_notifications(db=db, user=current_user, unread_only=unread_only)
    return success_response(
        data=[NotificationResponse.model_validate(n) for n in notifications],
        message="Notifications retrieved successfully"
    )

@notifications_router.put(
    "/{id}/read",
    summary="Mark Notification as Read"
)
def mark_notification_as_read(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Marks a specific user notification as read.
    """
    notification = NotificationService.mark_as_read(db=db, notification_id=id, user=current_user)
    return success_response(
        data=NotificationResponse.model_validate(notification),
        message="Notification marked as read successfully"
    )
