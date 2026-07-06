from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.financial_profile import FinancialProfileUpdate, FinancialProfileResponse
from app.services.financial_profile_service import FinancialProfileService
from app.utils.response_utils import success_response

financial_profile_router = APIRouter()

@financial_profile_router.get(
    "", 
    summary="Get Financial Profile"
)
def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves the flattened financial profile details for the authenticated user.
    """
    profile_data = FinancialProfileService.get_profile(db=db, user=current_user)
    return success_response(
        data=FinancialProfileResponse.model_validate(profile_data),
        message="Financial profile fetched successfully"
    )

@financial_profile_router.put(
    "", 
    summary="Update Financial Profile"
)
def update_profile(
    request: FinancialProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Updates the user's financial profile parameters (such as monthly income or expenses).
    """
    updated_data = FinancialProfileService.update_profile(
        db=db,
        user=current_user,
        profile_in=request
    )
    return success_response(
        data=FinancialProfileResponse.model_validate(updated_data),
        message="Financial profile updated successfully"
    )
