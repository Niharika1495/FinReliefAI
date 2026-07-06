from sqlalchemy.orm import Session
from typing import Dict, Any, List
from app.models.user import User
from app.models.loan import Loan
from app.models.ai_history import AIHistory
from app.models.settlement_recommendation import SettlementRecommendation
from app.services.financial_analysis_service import FinancialAnalysisService
from app.services.settlement_service import SettlementService

class DashboardService:
    """
    Service layer providing unified statistics aggregation for the user's dashboard.
    Coordinates metrics from financial health, loan liabilities, settlement options,
    and generative history without re-calculating formulas.
    """

    @staticmethod
    def get_overview(db: Session, user: User) -> Dict[str, Any]:
        """
        Compiles user details, health analysis stats, total active loans, surplus,
        eligible settlements, savings, and recent AI count.
        """
        # Call analysis and settlement services to get standard aggregates
        analysis = FinancialAnalysisService.calculate_analysis(db, user)
        settlement_recs = SettlementService.generate_recommendations(db, user)
        settlement_summary = SettlementService.generate_summary(db, user)

        # Count active loans
        loans = db.query(Loan).filter(Loan.user_id == user.id, Loan.is_active == True).all()
        total_active_loans = len(loans)
        
        total_outstanding = sum(l.outstanding_amount for l in loans)
        total_emi = sum(l.emi for l in loans)

        # Count recent AI requests
        recent_ai_activity_count = db.query(AIHistory).filter(AIHistory.user_id == user.id).count()

        return {
            "user_name": user.name,
            "financial_health_score": analysis["financial_health_score"],
            "risk_level": analysis["risk_level"],
            "repayment_capacity": analysis["repayment_capacity"],
            "monthly_income": user.monthly_income,
            "monthly_expenses": user.monthly_expenses,
            "monthly_surplus": analysis["monthly_surplus"],
            "total_active_loans": total_active_loans,
            "total_outstanding_amount": total_outstanding,
            "total_monthly_emi": total_emi,
            "eligible_settlements": settlement_summary["eligible_loans"],
            "estimated_savings": settlement_summary["total_savings"],
            "highest_priority_loan": settlement_summary["highest_priority_loan_lender"],
            "recent_ai_activity_count": recent_ai_activity_count
        }

    @staticmethod
    def get_financial_summary(db: Session, user: User) -> Dict[str, Any]:
        """
        Compiles monthly income, expenses, active EMIs, cash surplus, and health score.
        """
        analysis = FinancialAnalysisService.calculate_analysis(db, user)
        loans = db.query(Loan).filter(Loan.user_id == user.id, Loan.is_active == True).all()
        total_emi = sum(l.emi for l in loans)

        return {
            "income": user.monthly_income,
            "expenses": user.monthly_expenses,
            "emi": total_emi,
            "surplus": analysis["monthly_surplus"],
            "dti": analysis["dti_ratio"],
            "emi_ratio": analysis["emi_ratio"],
            "financial_score": analysis["financial_health_score"],
            "risk": analysis["risk_level"]
        }

    @staticmethod
    def get_loan_analytics(db: Session, user: User) -> Dict[str, Any]:
        """
        Compiles status and type distributions, outstanding balance split by lender,
        and rates averages.
        """
        loans = db.query(Loan).filter(Loan.user_id == user.id, Loan.is_active == True).all()
        settlement_summary = SettlementService.generate_summary(db, user)

        loan_count = len(loans)
        if loan_count == 0:
            return {
                "loan_count": 0,
                "outstanding_amount": 0.0,
                "average_interest_rate": 0.0,
                "highest_interest_rate": 0.0,
                "loan_type_distribution": {},
                "loan_status_distribution": {},
                "outstanding_amount_by_lender": {},
                "highest_priority_loan": None
            }

        outstanding_amount = sum(l.outstanding_amount for l in loans)
        rates = [l.interest_rate for l in loans]
        average_interest_rate = round(sum(rates) / loan_count, 2)
        highest_interest_rate = max(rates)

        loan_type_distribution = {}
        loan_status_distribution = {}
        outstanding_amount_by_lender = {}

        for l in loans:
            # Type distribution
            ltype = l.loan_type or "Unknown"
            loan_type_distribution[ltype] = loan_type_distribution.get(ltype, 0) + 1

            # Status distribution
            status_name = l.loan_status.value if hasattr(l.loan_status, "value") else str(l.loan_status)
            loan_status_distribution[status_name] = loan_status_distribution.get(status_name, 0) + 1

            # Lender split
            lender = l.lender_name
            outstanding_amount_by_lender[lender] = round(outstanding_amount_by_lender.get(lender, 0.0) + l.outstanding_amount, 2)

        return {
            "loan_count": loan_count,
            "outstanding_amount": outstanding_amount,
            "average_interest_rate": average_interest_rate,
            "highest_interest_rate": highest_interest_rate,
            "loan_type_distribution": loan_type_distribution,
            "loan_status_distribution": loan_status_distribution,
            "outstanding_amount_by_lender": outstanding_amount_by_lender,
            "highest_priority_loan": settlement_summary["highest_priority_loan_lender"]
        }

    @staticmethod
    def get_settlement_analytics(db: Session, user: User) -> Dict[str, Any]:
        """
        Compiles eligibility distributions, estimated savings aggregates, and difficulties.
        """
        recs = SettlementService.generate_recommendations(db, user)
        settlement_summary = SettlementService.generate_summary(db, user)

        eligible_loans = sum(1 for r in recs if r.eligibility == "ELIGIBLE")
        partially_eligible_loans = sum(1 for r in recs if r.eligibility == "PARTIALLY_ELIGIBLE")
        not_eligible_loans = sum(1 for r in recs if r.eligibility == "NOT_ELIGIBLE")

        negotiation_difficulty_distribution = {
            "LOW": 0,
            "MEDIUM": 0,
            "HIGH": 0,
            "VERY_HIGH": 0
        }
        for r in recs:
            difficulty = r.negotiation_difficulty or "LOW"
            negotiation_difficulty_distribution[difficulty] = negotiation_difficulty_distribution.get(difficulty, 0) + 1

        return {
            "eligible_loans": eligible_loans,
            "partially_eligible_loans": partially_eligible_loans,
            "not_eligible_loans": not_eligible_loans,
            "average_settlement_percentage": settlement_summary["average_settlement_percentage"],
            "total_estimated_savings": settlement_summary["total_savings"],
            "total_recommended_settlement": settlement_summary["total_recommended_settlement"],
            "negotiation_difficulty_distribution": negotiation_difficulty_distribution
        }

    @staticmethod
    def get_ai_analytics(db: Session, user: User) -> Dict[str, Any]:
        """
        Compiles prompt type distribution metrics and retrieves latest 10 log entries.
        """
        histories = db.query(AIHistory).filter(AIHistory.user_id == user.id).order_by(AIHistory.created_at.desc()).all()
        total_ai_requests = len(histories)

        negotiation_strategies_generated = sum(1 for h in histories if h.prompt_type == "negotiation_strategy")
        settlement_letters_generated = sum(1 for h in histories if h.prompt_type == "settlement_letter")
        negotiation_emails_generated = sum(1 for h in histories if h.prompt_type == "negotiation_email")
        financial_explanations_generated = sum(1 for h in histories if h.prompt_type == "financial_explanation")

        recent_ai_activities = histories[:10]

        return {
            "total_ai_requests": total_ai_requests,
            "negotiation_strategies_generated": negotiation_strategies_generated,
            "settlement_letters_generated": settlement_letters_generated,
            "negotiation_emails_generated": negotiation_emails_generated,
            "financial_explanations_generated": financial_explanations_generated,
            "recent_ai_activities": recent_ai_activities
        }

    @staticmethod
    def get_chart_data(db: Session, user: User) -> Dict[str, Any]:
        """
        Formats database statistics into list shapes ready to render in React charts libraries.
        """
        loans = db.query(Loan).filter(Loan.user_id == user.id, Loan.is_active == True).all()
        analysis = FinancialAnalysisService.calculate_analysis(db, user)
        recs = SettlementService.generate_recommendations(db, user)

        # Build raw distributions
        loan_type_dist = {}
        loan_status_dist = {}
        outstanding_by_lender_raw = {}
        
        for l in loans:
            ltype = l.loan_type or "Unknown"
            loan_type_dist[ltype] = loan_type_dist.get(ltype, 0.0) + 1.0

            status_name = l.loan_status.value if hasattr(l.loan_status, "value") else str(l.loan_status)
            loan_status_dist[status_name] = loan_status_dist.get(status_name, 0.0) + 1.0

            outstanding_by_lender_raw[l.lender_name] = round(outstanding_by_lender_raw.get(l.lender_name, 0.0) + l.outstanding_amount, 2)

        # 1. Loan Type Pie
        loan_type_pie_chart = [{"name": k, "value": v} for k, v in loan_type_dist.items()]

        # 2. Loan Status Pie
        loan_status_pie_chart = [{"name": k, "value": v} for k, v in loan_status_dist.items()]

        # 3. Interest Rate Bar Chart
        interest_rate_bar_chart = [{"lender_name": l.lender_name, "interest_rate": l.interest_rate} for l in loans]

        # 4. Outstanding by Lender Bar Chart
        outstanding_amount_by_lender = [{"lender_name": k, "outstanding_amount": v} for k, v in outstanding_by_lender_raw.items()]

        # 5. Settlement Eligibility Pie
        eligible_count = sum(1.0 for r in recs if r.eligibility == "ELIGIBLE")
        partial_count = sum(1.0 for r in recs if r.eligibility == "PARTIALLY_ELIGIBLE")
        not_eligible_count = sum(1.0 for r in recs if r.eligibility == "NOT_ELIGIBLE")
        
        settlement_eligibility_chart = [
            {"name": "ELIGIBLE", "value": eligible_count},
            {"name": "PARTIALLY_ELIGIBLE", "value": partial_count},
            {"name": "NOT_ELIGIBLE", "value": not_eligible_count}
        ]

        # 6. Score gauge
        financial_score_gauge_value = analysis["financial_health_score"]

        return {
            "loan_type_pie_chart": loan_type_pie_chart,
            "loan_status_pie_chart": loan_status_pie_chart,
            "interest_rate_bar_chart": interest_rate_bar_chart,
            "outstanding_amount_by_lender": outstanding_amount_by_lender,
            "settlement_eligibility_chart": settlement_eligibility_chart,
            "financial_score_gauge_value": financial_score_gauge_value
        }
