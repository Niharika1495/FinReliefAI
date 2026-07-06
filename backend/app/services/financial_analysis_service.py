from sqlalchemy.orm import Session
from typing import Dict, Any, List
from app.models.user import User
from app.models.loan import Loan
from app.models.financial_profile import FinancialProfile

class FinancialAnalysisService:
    """
    Service layer providing rule-based Financial Health Analysis,
    risk assessment, capacity determination, and recommendation compiling.
    Updates the database profile state concurrently.
    """

    @staticmethod
    def calculate_analysis(db: Session, user: User) -> Dict[str, Any]:
        """
        Executes complete rule-based analysis across user parameters and active loans.
        Saves updated stats to the user's FinancialProfile and returns standard payload.
        """
        # Query active user loans (ignore soft-deleted loans)
        loans = db.query(Loan).filter(Loan.user_id == user.id, Loan.is_active == True).all()

        # 1. Total Active Loans
        total_active_loans = len(loans)

        # 2. Total Outstanding Amount
        total_outstanding = sum(loan.outstanding_amount for loan in loans)

        # 3. Total Monthly EMI
        total_monthly_emi = sum(loan.emi for loan in loans)

        # 4 & 5. Monthly Income & Expenses
        monthly_income = user.monthly_income
        monthly_expenses = user.monthly_expenses

        # 6. Monthly Surplus
        monthly_surplus = monthly_income - monthly_expenses - total_monthly_emi

        # 7 & 8. Debt-To-Income (DTI) and EMI Ratios
        if monthly_income == 0.0:
            dti_ratio = 100.0
            emi_ratio = 100.0
        else:
            dti_ratio = round((total_monthly_emi / monthly_income) * 100.0, 2)
            emi_ratio = round((total_monthly_emi / monthly_income) * 100.0, 2)

        # 9, 10 & 11. Interest rates and Overdue Months
        if total_active_loans == 0:
            average_interest_rate = 0.0
            highest_interest_rate = 0.0
            maximum_overdue_months = 0
        else:
            interest_rates = [loan.interest_rate for loan in loans]
            average_interest_rate = round(sum(interest_rates) / total_active_loans, 2)
            highest_interest_rate = max(interest_rates)
            maximum_overdue_months = max(loan.overdue_months for loan in loans)

        # 12. Financial Health Score (Deterministic, bound between 0 and 100)
        # Base starts at 100
        score = 100.0

        # Subtractions:
        # DTI Penalty: DTI * 0.5 (capped at 50.0 points)
        dti_penalty = min(50.0, dti_ratio * 0.5)
        score -= dti_penalty

        # Outstanding Penalty: $5,000 outstanding = 1 point penalty (capped at 20.0 points)
        outstanding_penalty = min(20.0, total_outstanding / 5000.0)
        score -= outstanding_penalty

        # Overdue Penalty: 10 points per overdue month (capped at 30.0 points)
        overdue_penalty = min(30.0, float(maximum_overdue_months * 10))
        score -= overdue_penalty

        # High Interest Penalty: 5 points per loan with interest rate > 15.0% (capped at 15.0 points)
        high_interest_loans_count = sum(1 for loan in loans if loan.interest_rate > 15.0)
        high_interest_penalty = min(15.0, float(high_interest_loans_count * 5))
        score -= high_interest_penalty

        # Final health score bounding
        financial_health_score = round(max(0.0, min(100.0, score)), 2)

        # 13. Risk Level
        if financial_health_score >= 80.0:
            risk_level = "LOW"
        elif financial_health_score >= 60.0:
            risk_level = "MEDIUM"
        elif financial_health_score >= 40.0:
            risk_level = "HIGH"
        else:
            risk_level = "CRITICAL"

        # 14. Repayment Capacity
        if monthly_surplus > 1500.0 and dti_ratio < 30.0:
            repayment_capacity = "GOOD"
        elif monthly_surplus >= 500.0 and dti_ratio < 50.0:
            repayment_capacity = "MODERATE"
        elif monthly_surplus >= 0.0 and dti_ratio < 70.0:
            repayment_capacity = "WEAK"
        else:
            repayment_capacity = "VERY_WEAK"

        # 15. Recommendations Engine (Return between 3 and 5 items based on rules)
        triggered_recs = []

        if dti_ratio > 40.0:
            triggered_recs.append("Reduce discretionary spending to lower your debt-to-income ratio.")
        if highest_interest_rate > 15.0:
            triggered_recs.append("Prioritize paying off high-interest loans first to save on interest costs.")
        if maximum_overdue_months > 0:
            triggered_recs.append("Prioritize resolving overdue accounts to stop late penalties and protect credit history.")
        if monthly_surplus < 500.0:
            triggered_recs.append("Focus on building an emergency fund covering 3-6 months of expenses.")
        if total_active_loans > 3:
            triggered_recs.append("Avoid taking new loans to prevent further financial stress.")
        if monthly_surplus > 1000.0 and total_outstanding > 0.0:
            triggered_recs.append("Consider increasing your monthly repayment amount to pay down outstanding balance faster.")

        # Fallbacks list to fill the gap if triggered recommendations are fewer than 3
        fallbacks = [
            "Create a detailed monthly budget to track and control all categories of expenses.",
            "Avoid taking on any new consumer debt or credit lines.",
            "Consistently pay at least the minimum due on all active loan accounts."
        ]

        # Assemble final recommendations (minimum 3, maximum 5)
        recommendations = []
        for rec in triggered_recs:
            if len(recommendations) < 5:
                recommendations.append(rec)

        for fallback in fallbacks:
            if len(recommendations) < 3:
                if fallback not in recommendations:
                    recommendations.append(fallback)
            else:
                break

        # Persist calculations to the user's FinancialProfile record in database
        profile = user.financial_profile
        if not profile:
            profile = FinancialProfile(
                user_id=user.id,
                emi_ratio=emi_ratio,
                dti_ratio=dti_ratio,
                monthly_surplus=monthly_surplus,
                stress_level=risk_level
            )
            db.add(profile)
        else:
            profile.emi_ratio = emi_ratio
            profile.dti_ratio = dti_ratio
            profile.monthly_surplus = monthly_surplus
            profile.stress_level = risk_level

        db.commit()
        db.refresh(profile)

        return {
            "financial_health_score": financial_health_score,
            "risk_level": risk_level,
            "repayment_capacity": repayment_capacity,
            "monthly_income": monthly_income,
            "monthly_expenses": monthly_expenses,
            "monthly_surplus": monthly_surplus,
            "total_active_loans": total_active_loans,
            "total_outstanding": total_outstanding,
            "total_monthly_emi": total_monthly_emi,
            "dti_ratio": dti_ratio,
            "emi_ratio": emi_ratio,
            "average_interest_rate": average_interest_rate,
            "highest_interest_rate": highest_interest_rate,
            "maximum_overdue_months": maximum_overdue_months,
            "recommendations": recommendations
        }
