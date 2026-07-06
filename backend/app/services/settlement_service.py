import math
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Tuple
from app.models.user import User
from app.models.loan import Loan
from app.models.settlement_recommendation import SettlementRecommendation
from app.services.financial_analysis_service import FinancialAnalysisService

class SettlementService:
    """
    Service layer providing rule-based calculations for debt settlement recommendation options.
    Estimates optimal payoff schedules, negotiation difficulties, and aggregates priority rankings.
    """

    @staticmethod
    def calculate_settlement(loan: Loan, risk_level: str, dti: float, health_score: float) -> Tuple[str, float, float]:
        """
        Determines eligibility status, settlement percentage, and recommended payment amount.
        """
        # Eligibility Rules
        if loan.overdue_months >= 3 or dti > 60.0 or health_score < 50.0:
            eligibility = "ELIGIBLE"
        elif 40.0 <= dti <= 60.0:
            eligibility = "PARTIALLY_ELIGIBLE"
        else:
            eligibility = "NOT_ELIGIBLE"

        # Percentage Rules
        if risk_level == "CRITICAL":
            settlement_percentage = 50.0
        elif risk_level == "HIGH":
            settlement_percentage = 60.0
        elif risk_level == "MEDIUM":
            settlement_percentage = 70.0
        else:
            settlement_percentage = 90.0

        recommended_amount = round(loan.outstanding_amount * (settlement_percentage / 100.0), 2)
        return eligibility, settlement_percentage, recommended_amount

    @staticmethod
    def calculate_savings(loan: Loan, recommended_amount: float) -> float:
        """
        Calculates savings amount between outstanding balance and recommended settlement.
        """
        return round(loan.outstanding_amount - recommended_amount, 2)

    @staticmethod
    def calculate_payoff(loan: Loan, recommended_amount: float, monthly_surplus: float) -> int:
        """
        Forecasts payback timeline in months based on available surplus and loan EMI.
        """
        divisor = monthly_surplus + loan.emi
        if divisor > 0.0:
            return math.ceil(recommended_amount / divisor)
        return 60

    @staticmethod
    def calculate_priority(loan: Loan, risk_level: str) -> float:
        """
        Determines relative priority index from 0 to 100 based on interest, overdue, and balance metrics.
        """
        interest_points = min(30.0, loan.interest_rate * 1.5)
        overdue_points = min(30.0, float(loan.overdue_months * 10))
        outstanding_points = min(20.0, (loan.outstanding_amount / 5000.0) * 2.0)

        # Risk scoring impact
        if risk_level == "CRITICAL":
            risk_points = 15.0
        elif risk_level == "HIGH":
            risk_points = 10.0
        elif risk_level == "MEDIUM":
            risk_points = 5.0
        else:
            risk_points = 0.0

        # Loan type scoring weight (unsecured vs secured indicators)
        ltype = loan.loan_type.lower() if loan.loan_type else ""
        if "credit" in ltype or "card" in ltype:
            loan_type_points = 5.0
        elif "personal" in ltype:
            loan_type_points = 3.0
        elif "auto" in ltype or "car" in ltype:
            loan_type_points = 1.0
        else:
            loan_type_points = 0.0

        total_score = interest_points + overdue_points + outstanding_points + risk_points + loan_type_points
        return round(min(100.0, max(0.0, total_score)), 2)

    @staticmethod
    def generate_recommendations(db: Session, user: User, recalculate: bool = False) -> List[SettlementRecommendation]:
        """
        Retrieves or dynamically computes/saves all settlement recommendation options for active loans.
        """
        existing = db.query(SettlementRecommendation).filter(SettlementRecommendation.user_id == user.id).all()
        active_loans = db.query(Loan).filter(Loan.user_id == user.id, Loan.is_active == True).all()

        if existing and not recalculate:
            existing_loan_ids = {r.loan_id for r in existing}
            active_loan_ids = {l.id for l in active_loans}
            if existing_loan_ids == active_loan_ids:
                return existing

        # Clear outdated calculations
        db.query(SettlementRecommendation).filter(SettlementRecommendation.user_id == user.id).delete()
        db.commit()

        if not active_loans:
            return []

        # Run health check analysis
        analysis = FinancialAnalysisService.calculate_analysis(db, user)
        dti = analysis["dti_ratio"]
        health_score = analysis["financial_health_score"]
        risk_level = analysis["risk_level"]
        monthly_surplus = analysis["monthly_surplus"]

        recommendations = []
        for loan in active_loans:
            eligibility, pct, amt = SettlementService.calculate_settlement(loan, risk_level, dti, health_score)
            savings = SettlementService.calculate_savings(loan, amt)
            payoff_months = SettlementService.calculate_payoff(loan, amt, monthly_surplus)
            priority = SettlementService.calculate_priority(loan, risk_level)

            # Negotiation Difficulty scoring logic
            if loan.overdue_months >= 6 or loan.outstanding_amount > 20000.0 or loan.interest_rate > 20.0:
                difficulty = "VERY_HIGH"
            elif loan.overdue_months >= 3 or loan.outstanding_amount > 10000.0 or loan.interest_rate > 15.0:
                difficulty = "HIGH"
            elif loan.overdue_months >= 1 or loan.outstanding_amount > 5000.0 or loan.interest_rate > 10.0:
                difficulty = "MEDIUM"
            else:
                difficulty = "LOW"

            rec = SettlementRecommendation(
                user_id=user.id,
                loan_id=loan.id,
                eligibility=eligibility,
                settlement_percentage=pct,
                recommended_amount=amt,
                estimated_savings=savings,
                estimated_payoff_months=payoff_months,
                priority_score=priority,
                negotiation_difficulty=difficulty
            )
            db.add(rec)
            recommendations.append(rec)

        db.commit()
        for rec in recommendations:
            db.refresh(rec)

        return recommendations

    @staticmethod
    def generate_summary(db: Session, user: User) -> Dict[str, Any]:
        """
        Creates an aggregate summary dashboard metadata representation of computed loan items.
        """
        recs = db.query(SettlementRecommendation).filter(SettlementRecommendation.user_id == user.id).all()
        active_loans = db.query(Loan).filter(Loan.user_id == user.id, Loan.is_active == True).all()

        if not active_loans or not recs:
            return {
                "eligible_loans": 0,
                "average_settlement_percentage": 0.0,
                "total_savings": 0.0,
                "total_recommended_settlement": 0.0,
                "highest_priority_loan_id": None,
                "highest_priority_loan_lender": None,
                "recommendations": [
                    "Avoid taking new credit.",
                    "Create a dedicated savings plan for the recommended settlement amounts."
                ]
            }

        eligible_recs = [r for r in recs if r.eligibility in ("ELIGIBLE", "PARTIALLY_ELIGIBLE")]
        eligible_count = len(eligible_recs)

        if eligible_count > 0:
            avg_pct = round(sum(r.settlement_percentage for r in eligible_recs) / eligible_count, 2)
        else:
            avg_pct = 0.0

        total_savings = round(sum(r.estimated_savings for r in recs), 2)
        total_recommended_settlement = round(sum(r.recommended_amount for r in recs), 2)

        highest_rec = max(recs, key=lambda r: r.priority_score)
        highest_priority_loan_id = highest_rec.loan_id

        highest_loan = db.query(Loan).filter(Loan.id == highest_priority_loan_id).first()
        highest_priority_loan_lender = highest_loan.lender_name if highest_loan else None

        triggered_recs = []

        if highest_loan:
            triggered_recs.append(f"Negotiate the settlement for {highest_priority_loan_lender} first as it has the highest priority score of {highest_rec.priority_score}.")

        high_interest_loans = [l for l in active_loans if l.interest_rate > 15.0]
        if high_interest_loans:
            lenders = ", ".join(l.lender_name for l in high_interest_loans[:2])
            triggered_recs.append(f"Pay off high-interest loans like {lenders} immediately to reduce accrued interest.")

        overdue_loans = [l for l in active_loans if l.overdue_months >= 3]
        if overdue_loans:
            lenders = ", ".join(l.lender_name for l in overdue_loans[:2])
            triggered_recs.append(f"Clear overdue accounts like {lenders} before they default completely.")

        analysis = FinancialAnalysisService.calculate_analysis(db, user)
        surplus = analysis["monthly_surplus"]
        if surplus > 500.0:
            triggered_recs.append(f"Utilize your monthly surplus of ${surplus} toward your settlement payoff fund.")

        if len(active_loans) > 2:
            triggered_recs.append("Avoid taking new credit while settling your existing liabilities.")

        fallbacks = [
            "Create a dedicated savings plan for the recommended settlement amounts.",
            "Contact creditors proactively to discuss settlement terms.",
            "Stop using credit cards associated with accounts undergoing negotiation."
        ]

        recommendations = []
        for rec_str in triggered_recs:
            if len(recommendations) < 5:
                recommendations.append(rec_str)

        for fallback in fallbacks:
            if len(recommendations) < 3:
                if fallback not in recommendations:
                    recommendations.append(fallback)
            else:
                break

        return {
            "eligible_loans": eligible_count,
            "average_settlement_percentage": avg_pct,
            "total_savings": total_savings,
            "total_recommended_settlement": total_recommended_settlement,
            "highest_priority_loan_id": highest_priority_loan_id,
            "highest_priority_loan_lender": highest_priority_loan_lender,
            "recommendations": recommendations
        }
