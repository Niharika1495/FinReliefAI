import os
import time
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, Any, Tuple
from app.models.user import User
from app.services.loan_service import LoanService
from app.services.financial_analysis_service import FinancialAnalysisService
from app.services.settlement_service import SettlementService
from app.services.dashboard_service import DashboardService
from app.utils.pdf_generator import generate_pdf_report
from app.utils.csv_generator import generate_csv_report
from app.utils.exceptions import FinReliefException

REPORTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static", "reports"))

class ReportService:
    """
    Service layer providing unified PDF and CSV exports for user profiles and analytics logs.
    """

    @staticmethod
    def _ensure_reports_dir():
        """
        Guarantees that the temporary static reports directory cache exists.
        """
        os.makedirs(REPORTS_DIR, exist_ok=True)

    @staticmethod
    def cleanup_old_reports(max_age_seconds: int = 3600):
        """
        Scans reports cache folder and purges temp documents older than threshold (1 hour).
        """
        if not os.path.exists(REPORTS_DIR):
            return
        now = time.time()
        for filename in os.listdir(REPORTS_DIR):
            file_path = os.path.join(REPORTS_DIR, filename)
            if os.path.isfile(file_path):
                # Check creation/modified age
                if now - os.path.getmtime(file_path) > max_age_seconds:
                    try:
                        os.remove(file_path)
                    except Exception:
                        pass

    @staticmethod
    def _compile_report_data(db: Session, user: User, report_type: str) -> Tuple[str, dict]:
        """
        Gathers metric datasets from existing services based on the requested report context.
        """
        ReportService.cleanup_old_reports() # Run proactive cleanup on generation trigger

        if report_type == "financial":
            # Financial profile summary
            analysis = FinancialAnalysisService.calculate_analysis(db, user)
            profile_data = {
                "Monthly Income": user.monthly_income,
                "Monthly Expenses": user.monthly_expenses,
                "Debt-to-Income (DTI) %": f"{analysis['dti_ratio']:.1f}%",
                "EMI Ratio %": f"{analysis['emi_ratio']:.1f}%",
                "Financial Health Score": analysis["financial_health_score"],
                "Assessed Risk Level": analysis["risk_level"],
                "Calculated Repayment Capacity": analysis["repayment_capacity"]
            }
            return "Financial Health Report", {
                "User Financial Profile Metrics": profile_data
            }

        elif report_type == "dashboard":
            # Dashboard Overview Metrics
            overview = DashboardService.get_overview(db, user)
            charts = DashboardService.get_chart_data(db, user)
            
            summary_info = {
                "User Name": overview["user_name"],
                "Health Score": overview["financial_health_score"],
                "Risk Rating": overview["risk_level"],
                "EMI Sum": overview["total_monthly_emi"],
                "Outstanding Debt Sum": overview["total_outstanding_amount"],
                "Active Loans Count": overview["total_active_loans"],
                "AI History Log Entries": overview["recent_ai_activity_count"]
            }
            
            loans_list = []
            loans = LoanService.get_loans(db, user)
            for l in loans:
                loans_list.append({
                    "lender": l.lender_name,
                    "type": l.loan_type,
                    "balance": l.outstanding_amount,
                    "rate": f"{l.interest_rate}%",
                    "emi": l.emi,
                    "status": l.loan_status.value
                })
                
            return "Dashboard Metrics Summary", {
                "General Analytics Overview": summary_info,
                "Active Registered Liabilities": loans_list
            }

        elif report_type == "settlement":
            # Settlement recommendations
            recs = SettlementService.generate_recommendations(db, user)
            summary = SettlementService.generate_summary(db, user)
            
            summary_info = {
                "Eligible Target Loans": summary["eligible_loans"],
                "Estimated Total Savings": summary["total_savings"],
                "Recommended Settlement Total": summary["total_recommended_settlement"],
                "Average Proposed Percentage": f"{summary['average_settlement_percentage']}%",
                "Priority Target Lender": summary["highest_priority_loan_lender"] or "None"
            }
            
            recs_list = []
            for r in recs:
                recs_list.append({
                    "lender": r.loan.lender_name,
                    "eligibility": r.eligibility,
                    "percentage": f"{r.settlement_percentage}%",
                    "target_amount": r.recommended_amount,
                    "savings": r.estimated_savings,
                    "difficulty": r.negotiation_difficulty
                })
                
            return "Debt Settlement Strategy Report", {
                "Settlement Summary Metrics": summary_info,
                "Settlement Options and Recommendations": recs_list
            }

        elif report_type == "loans":
            # Direct Loans list report
            loans = LoanService.get_loans(db, user)
            loans_list = []
            total_outstanding = 0.0
            total_emi = 0.0
            
            for l in loans:
                total_outstanding += l.outstanding_amount
                total_emi += l.emi
                loans_list.append({
                    "lender": l.lender_name,
                    "type": l.loan_type,
                    "outstanding_amount": l.outstanding_amount,
                    "interest_rate": f"{l.interest_rate}%",
                    "emi": l.emi,
                    "overdue_months": l.overdue_months,
                    "status": l.loan_status.value
                })
                
            summary_info = {
                "Total Loans Count": len(loans),
                "Total Outstanding Debt": total_outstanding,
                "Total Monthly EMIs": total_emi
            }
            return "User Liability Statement", {
                "Loans Aggregated Statistics": summary_info,
                "Detailed Liabilities Account Registry": loans_list
            }

        else:
            raise FinReliefException(
                status_code=400,
                error_code="INVALID_REPORT_TYPE",
                message=f"Unsupported report type: {report_type}"
            )

    @staticmethod
    def generate_report_file(db: Session, user: User, report_type: str, file_format: str) -> str:
        """
        Compiles the report data and generates the export file (PDF or CSV).
        Returns the absolute filepath.
        """
        ReportService._ensure_reports_dir()
        title, report_data = ReportService._compile_report_data(db, user, report_type)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{report_type}_report_{user.id}_{timestamp}.{file_format}"
        file_path = os.path.join(REPORTS_DIR, filename)
        
        if file_format == "pdf":
            generate_pdf_report(file_path, title, report_data)
        elif file_format == "csv":
            generate_csv_report(file_path, report_data)
        else:
            raise FinReliefException(
                status_code=400,
                error_code="INVALID_EXPORT_FORMAT",
                message=f"Unsupported export format: {file_format}"
            )
            
        return file_path
