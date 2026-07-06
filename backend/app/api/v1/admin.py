from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.dependencies.db import get_db
from app.dependencies.admin_auth import get_current_admin
from app.models.admin import Admin
from app.models.user import User
from app.models.loan import Loan
from app.models.audit_log import AuditLog
from app.schemas.admin import AdminLoginRequest, AdminTokenResponse, AdminDashboardMetrics
from app.schemas.user import UserResponse
from app.schemas.loan import LoanResponse
from app.services.admin_service import AdminService
from app.utils.response_utils import success_response
from app.services.audit_service import AuditService

admin_router = APIRouter()

@admin_router.post(
    "/login",
    response_model=None,
    summary="Authenticate Administrator"
)
def login_admin(
    request: AdminLoginRequest,
    db: Session = Depends(get_db)
):
    """
    Verifies admin credentials and returns a secure JWT access token.
    """
    token = AdminService.authenticate_admin(db=db, username=request.username, password=request.password)
    
    # Audit log entry for administrator login
    AuditService.create_log(
        db=db,
        user_id=None,
        action=f"Admin login: {request.username}"
    )

    return success_response(
        data={"access_token": token, "token_type": "bearer"},
        message="Admin authenticated successfully"
    )

@admin_router.get(
    "/dashboard",
    response_model=None,
    summary="Retrieve Admin Health & Analytics Metrics Dashboard"
)
def get_dashboard(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Unified analytics endpoint retrieving health metrics and performance statistics.
    """
    metrics = AdminService.get_dashboard_metrics(db=db)
    return success_response(
        data=metrics,
        message="Admin metrics compiled successfully"
    )

@admin_router.get(
    "/users",
    response_model=None,
    summary="List System Users"
)
def list_users(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Retrieves all registered system users for admin review.
    """
    users = db.query(User).order_by(User.created_at.desc()).all()
    return success_response(
        data=[UserResponse.model_validate(u) for u in users],
        message="Users list retrieved successfully"
    )

@admin_router.get(
    "/loans",
    response_model=None,
    summary="List System Loans"
)
def list_loans(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Retrieves all registered active/inactive loans for administrative auditing.
    """
    loans = db.query(Loan).order_by(Loan.created_at.desc()).all()
    return success_response(
        data=[LoanResponse.model_validate(l) for l in loans],
        message="Loans list retrieved successfully"
    )

@admin_router.get(
    "/audit-logs",
    response_model=None,
    summary="List Administrative Audit History Logs"
)
def list_audit_logs(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin)
):
    """
    Retrieves execution logs, request tracking records, and mutation audits.
    """
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).all()
    serialized_logs = []
    for log in logs:
        serialized_logs.append({
            "id": log.id,
            "user_id": log.user_id,
            "timestamp": log.timestamp.isoformat(),
            "action": log.action,
            "ip_address": log.ip_address,
            "endpoint": log.endpoint,
            "request_id": log.request_id
        })
    return success_response(
        data=serialized_logs,
        message="Audit logs retrieved successfully"
    )
