from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.settlement_service import SettlementService
from app.schemas.settlement_recommendation import SettlementRecommendationResponse, SettlementSummaryResponse
from app.utils.response_utils import success_response
from app.utils.exceptions import FinReliefException

settlement_router = APIRouter()

@settlement_router.get(
    "",
    summary="Get All Loan Settlement Recommendations",
    response_model=None
)
def get_settlements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves or generates computed rule-based settlement recommendations for all
    active user loan lines.
    """
    recs = SettlementService.generate_recommendations(db=db, user=current_user)
    serialized_recs = [SettlementRecommendationResponse.model_validate(r) for r in recs]
    return success_response(
        data=serialized_recs,
        message="Settlement recommendations retrieved successfully.",
        status_code=status.HTTP_200_OK
    )

@settlement_router.get(
    "/summary",
    summary="Get Settlement Recommendation Summary",
    response_model=None
)
def get_settlement_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves aggregated summary statistics for the user's settlement plan.
    """
    # Ensure recommendations are initialized
    SettlementService.generate_recommendations(db=db, user=current_user)
    summary_data = SettlementService.generate_summary(db=db, user=current_user)
    return success_response(
        data=SettlementSummaryResponse.model_validate(summary_data),
        message="Settlement summary retrieved successfully.",
        status_code=status.HTTP_200_OK
    )

@settlement_router.get(
    "/{loan_id}",
    summary="Get Specific Loan Settlement Recommendation",
    response_model=None
)
def get_settlement_by_loan(
    loan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves computed recommendation details for a single loan resource.
    Validates ownership of both the loan and the recommendation parameters.
    """
    # Force recommendation calculations first
    recs = SettlementService.generate_recommendations(db=db, user=current_user)
    
    # Locate the target record
    target_rec = None
    for r in recs:
        if r.loan_id == loan_id:
            target_rec = r
            break
            
    if not target_rec:
        raise FinReliefException(
            message="Settlement recommendation not found for this loan.",
            code="RECOMMENDATION_NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND
        )

    # Double check ownership verification
    if target_rec.user_id != current_user.id:
        raise FinReliefException(
            message="You do not have permission to access this recommendation.",
            code="FORBIDDEN",
            status_code=status.HTTP_403_FORBIDDEN
        )

    return success_response(
        data=SettlementRecommendationResponse.model_validate(target_rec),
        message="Settlement recommendation retrieved successfully.",
        status_code=status.HTTP_200_OK
    )

@settlement_router.post(
    "/recalculate",
    summary="Recalculate Loan Settlement Recommendations",
    response_model=None
)
def recalculate_settlements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Forces recalculation of all settlement recommendation options for active user loans.
    """
    recs = SettlementService.generate_recommendations(db=db, user=current_user, recalculate=True)
    serialized_recs = [SettlementRecommendationResponse.model_validate(r) for r in recs]
    return success_response(
        data=serialized_recs,
        message="Settlement recommendations regenerated successfully.",
        status_code=status.HTTP_200_OK
    )
