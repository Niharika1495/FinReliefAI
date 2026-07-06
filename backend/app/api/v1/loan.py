from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.loan import LoanCreate, LoanUpdate, LoanResponse
from app.services.loan_service import LoanService
from app.utils.response_utils import success_response

loan_router = APIRouter()

@loan_router.post(
    "", 
    status_code=status.HTTP_201_CREATED,
    summary="Create New Loan"
)
def create_loan(
    request: LoanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Creates a new loan record under the authenticated user session.
    """
    loan = LoanService.create_loan(db=db, loan_in=request, user_id=current_user.id)
    return success_response(
        data=LoanResponse.model_validate(loan),
        message="Loan created successfully",
        status_code=status.HTTP_201_CREATED
    )

@loan_router.get(
    "", 
    summary="List Active User Loans"
)
def get_loans(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    sort_by: str = Query("created_at"),
    order: str = Query("desc"),
    loan_type: Optional[str] = Query(None),
    lender_name: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves a paginated list of active, non-deleted loans for the user,
    with options for sorting and filtering.
    """
    result = LoanService.get_user_loans(
        db=db,
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        order=order,
        loan_type=loan_type,
        lender_name=lender_name
    )
    
    # Serialize items list using LoanResponse schema
    result["items"] = [LoanResponse.model_validate(item) for item in result["items"]]
    
    return success_response(
        data=result,
        message="Loans fetched successfully"
    )

@loan_router.get(
    "/summary", 
    summary="Get Loans Aggregates Summary"
)
def get_loan_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Compiles aggregate totals and statistics from the user's active loans.
    """
    summary = LoanService.get_loan_summary(db=db, user_id=current_user.id)
    return success_response(
        data=summary,
        message="Loan summary fetched successfully"
    )

@loan_router.get(
    "/{loan_id}", 
    summary="Get Loan Details"
)
def get_loan(
    loan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Fetches details for a specific user loan by ID.
    """
    loan = LoanService.get_loan(db=db, loan_id=loan_id, user_id=current_user.id)
    return success_response(
        data=LoanResponse.model_validate(loan),
        message="Loan fetched successfully"
    )

@loan_router.put(
    "/{loan_id}", 
    summary="Update Loan"
)
def update_loan(
    loan_id: int,
    request: LoanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Updates properties on an existing active loan record.
    """
    loan = LoanService.update_loan(
        db=db,
        loan_id=loan_id,
        loan_in=request,
        user_id=current_user.id
    )
    return success_response(
        data=LoanResponse.model_validate(loan),
        message="Loan updated successfully"
    )

@loan_router.delete(
    "/{loan_id}", 
    summary="Soft Delete Loan"
)
def delete_loan(
    loan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Performs a soft delete on a user's loan, removing it from normal lookups.
    """
    LoanService.soft_delete_loan(db=db, loan_id=loan_id, user_id=current_user.id)
    return success_response(
        message="Loan deleted successfully"
    )
