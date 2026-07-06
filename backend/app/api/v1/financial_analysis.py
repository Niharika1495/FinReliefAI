from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.financial_analysis_service import FinancialAnalysisService
from app.schemas.financial_analysis import FinancialAnalysisResponse
from app.utils.response_utils import success_response

financial_analysis_router = APIRouter()

@financial_analysis_router.get(
    "",
    summary="Get Financial Health Analysis",
    response_model=None
)
def get_financial_analysis(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Computes and returns the standard financial health analysis payload
    for the authenticated user.
    """
    analysis_data = FinancialAnalysisService.calculate_analysis(db=db, user=current_user)
    return success_response(
        data=FinancialAnalysisResponse.model_validate(analysis_data),
        message="Financial analysis generated successfully.",
        status_code=status.HTTP_200_OK
    )

@financial_analysis_router.post(
    "/recalculate",
    summary="Recalculate Financial Health Analysis",
    response_model=None
)
def recalculate_financial_analysis(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Recalculates the user's financial health analysis metrics and
    returns the updated payload.
    """
    analysis_data = FinancialAnalysisService.calculate_analysis(db=db, user=current_user)
    return success_response(
        data=FinancialAnalysisResponse.model_validate(analysis_data),
        message="Financial analysis generated successfully.",
        status_code=status.HTTP_200_OK
    )
