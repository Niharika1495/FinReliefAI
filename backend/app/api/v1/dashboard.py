from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.dashboard_service import DashboardService
from app.schemas.dashboard import (
    DashboardOverviewResponse,
    FinancialSummaryResponse,
    LoanAnalyticsResponse,
    SettlementAnalyticsResponse,
    AIAnalyticsResponse,
    ChartDataResponse
)
from app.utils.response_utils import success_response

dashboard_router = APIRouter()

@dashboard_router.get(
    "/overview",
    summary="Get Dashboard Overview Aggregates",
    response_model=None
)
def get_dashboard_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves the user's base dashboard overview profile card aggregates.
    """
    data = DashboardService.get_overview(db=db, user=current_user)
    return success_response(
        data=DashboardOverviewResponse.model_validate(data),
        message="Dashboard overview retrieved successfully.",
        status_code=status.HTTP_200_OK
    )

@dashboard_router.get(
    "/financial-summary",
    summary="Get Financial Summary Metrics",
    response_model=None
)
def get_financial_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves aggregated summary statistics of income, expenses, and cash surplus.
    """
    data = DashboardService.get_financial_summary(db=db, user=current_user)
    return success_response(
        data=FinancialSummaryResponse.model_validate(data),
        message="Financial summary retrieved successfully.",
        status_code=status.HTTP_200_OK
    )

@dashboard_router.get(
    "/loan-analytics",
    summary="Get Liability Analytics Distributions",
    response_model=None
)
def get_loan_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves distributions of loan types, status codes, and interest averages.
    """
    data = DashboardService.get_loan_analytics(db=db, user=current_user)
    return success_response(
        data=LoanAnalyticsResponse.model_validate(data),
        message="Loan analytics retrieved successfully.",
        status_code=status.HTTP_200_OK
    )

@dashboard_router.get(
    "/settlement-analytics",
    summary="Get Settlement Target Metrics",
    response_model=None
)
def get_settlement_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves eligibility partitions, total target savings, and difficulties.
    """
    data = DashboardService.get_settlement_analytics(db=db, user=current_user)
    return success_response(
        data=SettlementAnalyticsResponse.model_validate(data),
        message="Settlement analytics retrieved successfully.",
        status_code=status.HTTP_200_OK
    )

@dashboard_router.get(
    "/ai-analytics",
    summary="Get AI Generation Auditing Logs",
    response_model=None
)
def get_ai_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves count of document types generated and lists the latest 10 log entries.
    """
    data = DashboardService.get_ai_analytics(db=db, user=current_user)
    return success_response(
        data=AIAnalyticsResponse.model_validate(data),
        message="AI analytics retrieved successfully.",
        status_code=status.HTTP_200_OK
    )

@dashboard_router.get(
    "/charts",
    summary="Get Visualization-Friendly Chart Payload",
    response_model=None
)
def get_chart_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Prepares and compiles formatted chart records ready to render in the UI.
    """
    data = DashboardService.get_chart_data(db=db, user=current_user)
    return success_response(
        data=ChartDataResponse.model_validate(data),
        message="Chart data retrieved successfully.",
        status_code=status.HTTP_200_OK
    )
