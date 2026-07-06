import math
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.loan import Loan, LoanStatus
from app.schemas.loan import LoanCreate, LoanUpdate
from app.utils.exceptions import FinReliefException

class LoanService:
    """
    Service layer providing CRUD operations and business calculations for User Loans.
    All operations are restricted by authentication and user ownership checks.
    """

    SORT_WHITELIST = {
        "created_at",
        "interest_rate",
        "outstanding_amount",
        "emi",
        "loan_type",
        "lender_name"
    }

    @staticmethod
    def create_loan(db: Session, loan_in: LoanCreate, user_id: int) -> Loan:
        """
        Creates a new Loan record mapped to the authenticated user context.
        """
        db_loan = Loan(
            user_id=user_id,
            lender_name=loan_in.lender_name,
            loan_type=loan_in.loan_type,
            outstanding_amount=loan_in.outstanding_amount,
            interest_rate=loan_in.interest_rate,
            emi=loan_in.emi,
            overdue_months=loan_in.overdue_months,
            is_active=True,
            loan_status=LoanStatus.ACTIVE
        )
        db.add(db_loan)
        db.commit()
        db.refresh(db_loan)
        return db_loan

    @staticmethod
    def get_user_loans(
        db: Session,
        user_id: int,
        page: int = 1,
        page_size: int = 10,
        sort_by: str = "created_at",
        order: str = "desc",
        loan_type: Optional[str] = None,
        lender_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fetches a paginated, sorted, and filtered list of active loans for a user.
        Raises HTTP 400 validation error if sorting by a non-whitelisted field.
        """
        # Validate sorting fields
        if sort_by not in LoanService.SORT_WHITELIST:
            raise FinReliefException(
                message=f"Sorting by field '{sort_by}' is not allowed. Choose from: {', '.join(sorted(LoanService.SORT_WHITELIST))}",
                code="INVALID_SORT_FIELD",
                status_code=400
            )

        query = db.query(Loan).filter(Loan.user_id == user_id, Loan.is_active == True)

        # Apply Filters
        if loan_type:
            query = query.filter(Loan.loan_type == loan_type)
        if lender_name:
            query = query.filter(Loan.lender_name == lender_name)

        # Count Total Matches
        total_items = query.count()

        # Apply Sorting
        sort_col = getattr(Loan, sort_by)
        if order.lower() == "asc":
            query = query.order_by(sort_col.asc())
        else:
            query = query.order_by(sort_col.desc())

        # Apply Pagination
        offset = (page - 1) * page_size
        items = query.offset(offset).limit(page_size).all()

        total_pages = math.ceil(total_items / page_size) if page_size > 0 else 0

        return {
            "items": items,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_items": total_items,
                "total_pages": total_pages
            }
        }

    @staticmethod
    def get_loan(db: Session, loan_id: int, user_id: int) -> Loan:
        """
        Fetches a specific loan. Verifies user ownership and checks that the loan is active.
        """
        loan = db.query(Loan).filter(Loan.id == loan_id).first()
        
        # Check existence and soft-delete status
        if not loan or not loan.is_active:
            raise FinReliefException(
                message="Loan record not found.",
                code="LOAN_NOT_FOUND",
                status_code=404
            )
            
        # Verify ownership
        if loan.user_id != user_id:
            raise FinReliefException(
                message="You do not have permission to access this loan.",
                code="FORBIDDEN",
                status_code=403
            )
            
        return loan

    @staticmethod
    def update_loan(db: Session, loan_id: int, loan_in: LoanUpdate, user_id: int) -> Loan:
        """
        Updates an existing loan's fields. Validates ownership and soft-delete state first.
        """
        db_loan = LoanService.get_loan(db, loan_id, user_id)
        
        # Apply updates
        update_data = loan_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_loan, field, value)
            
        db_loan.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(db_loan)
        return db_loan

    @staticmethod
    def soft_delete_loan(db: Session, loan_id: int, user_id: int) -> None:
        """
        Performs a soft delete of a loan record. Sets is_active = False.
        """
        db_loan = LoanService.get_loan(db, loan_id, user_id)
        db_loan.is_active = False
        db_loan.deleted_at = datetime.utcnow()
        db_loan.updated_at = datetime.utcnow()
        db.commit()

    @staticmethod
    def get_loan_summary(db: Session, user_id: int) -> Dict[str, Any]:
        """
        Gathers key summary statistics from all active (non-soft-deleted) loans for a user.
        """
        loans = db.query(Loan).filter(Loan.user_id == user_id, Loan.is_active == True).all()

        total_loans = len(loans)
        if total_loans == 0:
            return {
                "total_loans": 0,
                "active_loans": 0,
                "closed_loans": 0,
                "settled_loans": 0,
                "defaulted_loans": 0,
                "total_outstanding": 0.0,
                "total_emi": 0.0,
                "highest_interest_rate": 0.0,
                "average_interest_rate": 0.0,
                "oldest_overdue_months": 0
            }

        # Status breakdowns
        active_loans = sum(1 for l in loans if l.loan_status == LoanStatus.ACTIVE)
        closed_loans = sum(1 for l in loans if l.loan_status == LoanStatus.CLOSED)
        settled_loans = sum(1 for l in loans if l.loan_status == LoanStatus.SETTLED)
        defaulted_loans = sum(1 for l in loans if l.loan_status == LoanStatus.DEFAULTED)

        total_outstanding = sum(l.outstanding_amount for l in loans)
        total_emi = sum(l.emi for l in loans)
        
        interest_rates = [l.interest_rate for l in loans]
        highest_interest_rate = max(interest_rates)
        average_interest_rate = round(sum(interest_rates) / total_loans, 2)
        
        oldest_overdue_months = max(l.overdue_months for l in loans)

        return {
            "total_loans": total_loans,
            "active_loans": active_loans,
            "closed_loans": closed_loans,
            "settled_loans": settled_loans,
            "defaulted_loans": defaulted_loans,
            "total_outstanding": total_outstanding,
            "total_emi": total_emi,
            "highest_interest_rate": highest_interest_rate,
            "average_interest_rate": average_interest_rate,
            "oldest_overdue_months": oldest_overdue_months
        }
