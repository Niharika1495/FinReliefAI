from sqlalchemy.orm import Session
from app.models.user import User
from app.models.financial_profile import FinancialProfile
from app.schemas.financial_profile import FinancialProfileUpdate

class FinancialProfileService:
    """
    Service layer providing CRUD operations and profile status compilation.
    Aggregates profile attributes with basic income parameters defined on the User record.
    """

    @staticmethod
    def get_profile(db: Session, user: User) -> dict:
        """
        Compiles and returns a flattened dictionary representation of the user's financial profile.
        Automatically instantiates a default profile record if one does not exist.
        """
        profile = user.financial_profile
        if not profile:
            profile = FinancialProfile(
                user_id=user.id,
                emi_ratio=0.0,
                dti_ratio=0.0,
                monthly_surplus=user.monthly_income - user.monthly_expenses,
                stress_level="low"
            )
            db.add(profile)
            db.commit()
            db.refresh(profile)

        return {
            "id": profile.id,
            "user_id": profile.user_id,
            "monthly_income": user.monthly_income,
            "monthly_expenses": user.monthly_expenses,
            "emi_ratio": profile.emi_ratio,
            "dti_ratio": profile.dti_ratio,
            "monthly_surplus": profile.monthly_surplus,
            "stress_level": profile.stress_level,
            "created_at": profile.created_at,
            "updated_at": profile.updated_at
        }

    @staticmethod
    def update_profile(db: Session, user: User, profile_in: FinancialProfileUpdate) -> dict:
        """
        Updates the user's financial parameters (monthly income/expenses on the User record)
        and profile attributes (stress level on the FinancialProfile record).
        """
        # Trigger profile fetch/create
        FinancialProfileService.get_profile(db, user)
        profile = user.financial_profile

        # Apply User updates
        if profile_in.monthly_income is not None:
            user.monthly_income = profile_in.monthly_income
        if profile_in.monthly_expenses is not None:
            user.monthly_expenses = profile_in.monthly_expenses

        # Apply Profile updates
        if profile_in.stress_level is not None:
            profile.stress_level = profile_in.stress_level

        # Recompute basic monthly surplus
        profile.monthly_surplus = user.monthly_income - user.monthly_expenses

        db.commit()
        db.refresh(user)
        db.refresh(profile)

        return FinancialProfileService.get_profile(db, user)
