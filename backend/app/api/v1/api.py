from fastapi import APIRouter
from app.core.settings import settings
from app.api.v1.auth import auth_router
from app.api.v1.loan import loan_router
from app.api.v1.financial_profile import financial_profile_router
from app.api.v1.financial_analysis import financial_analysis_router
from app.api.v1.settlement import settlement_router
from app.api.v1.ai import ai_router
from app.api.v1.dashboard import dashboard_router
from app.api.v1.reports import reports_router
from app.api.v1.notifications import notifications_router
from app.api.v1.documents import documents_router
from app.api.v1.admin import admin_router

# Create version 1 router
api_router = APIRouter()

# Register endpoints
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(loan_router, prefix="/loans", tags=["loans"])
api_router.include_router(financial_profile_router, prefix="/financial-profile", tags=["financial-profile"])
api_router.include_router(financial_analysis_router, prefix="/financial-analysis", tags=["financial-analysis"])
api_router.include_router(settlement_router, prefix="/settlement", tags=["settlement"])
api_router.include_router(ai_router, prefix="/ai", tags=["ai"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(reports_router, prefix="/reports", tags=["reports"])
api_router.include_router(notifications_router, prefix="/notifications", tags=["notifications"])
api_router.include_router(documents_router, prefix="/documents", tags=["documents"])
api_router.include_router(admin_router, prefix="/admin", tags=["admin"])

@api_router.get("/", summary="V1 API Root")
async def get_root() -> dict:
    """
    Returns general app status details.
    """
    return {
        "message": "FinRelief AI Backend Running"
    }

@api_router.get("/health", summary="V1 API Health Status")
async def get_health() -> dict:
    """
    Returns application health check metrics and version values.
    """
    return {
        "status": "healthy",
        "version": settings.VERSION
    }
