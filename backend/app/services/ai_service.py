from sqlalchemy.orm import Session
from typing import List
from app.models.user import User
from app.models.loan import Loan
from app.models.ai_history import AIHistory
from app.schemas.ai import NegotiationRequest
from app.services.loan_service import LoanService
from app.services.financial_analysis_service import FinancialAnalysisService
from app.services.settlement_service import SettlementService
from app.ai.gemini_client import GeminiClient
from app.ai.prompts import (
    NEGOTIATION_STRATEGY_PROMPT,
    SETTLEMENT_LETTER_PROMPT,
    NEGOTIATION_EMAIL_PROMPT,
    FINANCIAL_EXPLANATION_PROMPT
)
from app.utils.exceptions import FinReliefException

class AIService:
    """
    AI Orchestrator Service.
    Coordinates database state gathering, prompt interpolation, calling the Gemini API Client,
    and auditing generation outcomes in the AIHistory table.
    """

    @staticmethod
    def generate_negotiation_strategy(db: Session, user: User, request_in: NegotiationRequest, api_key: str = None) -> dict:
        """
        Coordinates generating a professional negotiation guide step-by-step strategy for a loan.
        """
        loan = LoanService.get_loan(db, request_in.loan_id, user.id)
        analysis = FinancialAnalysisService.calculate_analysis(db, user)
        recs = SettlementService.generate_recommendations(db, user)
        
        target_rec = next((r for r in recs if r.loan_id == loan.id), None)
        if not target_rec:
            raise FinReliefException(
                message="Settlement recommendation not found for this loan.",
                code="RECOMMENDATION_NOT_FOUND",
                status_code=404
            )

        hardship = request_in.custom_hardship_description or "Borrower is experiencing severe financial hardship and cash surplus constraints making full repayment unfeasible."
        
        prompt = NEGOTIATION_STRATEGY_PROMPT.format(
            name=user.name,
            lender_name=loan.lender_name,
            loan_type=loan.loan_type,
            outstanding_amount=loan.outstanding_amount,
            interest_rate=loan.interest_rate,
            overdue_months=loan.overdue_months,
            recommended_amount=target_rec.recommended_amount,
            settlement_percentage=target_rec.settlement_percentage,
            estimated_savings=target_rec.estimated_savings,
            negotiation_difficulty=target_rec.negotiation_difficulty,
            hardship_description=hardship
        )

        response_text = GeminiClient.generate_content_with_retry(prompt, api_key=api_key)

        history = AIHistory(
            user_id=user.id,
            loan_id=loan.id,
            prompt_type="negotiation_strategy",
            prompt=prompt,
            response=response_text
        )
        db.add(history)
        db.commit()
        db.refresh(history)

        return {
            "loan_id": loan.id,
            "strategy": response_text
        }

    @staticmethod
    def generate_settlement_letter(db: Session, user: User, request_in: NegotiationRequest, api_key: str = None) -> dict:
        """
        Coordinates generating a formal debt settlement proposal letter.
        """
        loan = LoanService.get_loan(db, request_in.loan_id, user.id)
        analysis = FinancialAnalysisService.calculate_analysis(db, user)
        recs = SettlementService.generate_recommendations(db, user)
        
        target_rec = next((r for r in recs if r.loan_id == loan.id), None)
        if not target_rec:
            raise FinReliefException(
                message="Settlement recommendation not found for this loan.",
                code="RECOMMENDATION_NOT_FOUND",
                status_code=404
            )

        hardship = request_in.custom_hardship_description or "Borrower is experiencing severe financial hardship and cash surplus constraints making full repayment unfeasible."
        
        prompt = SETTLEMENT_LETTER_PROMPT.format(
            name=user.name,
            lender_name=loan.lender_name,
            loan_type=loan.loan_type,
            outstanding_amount=loan.outstanding_amount,
            emi=loan.emi,
            overdue_months=loan.overdue_months,
            recommended_amount=target_rec.recommended_amount,
            settlement_percentage=target_rec.settlement_percentage,
            hardship_description=hardship
        )

        response_text = GeminiClient.generate_content_with_retry(prompt, api_key=api_key)

        history = AIHistory(
            user_id=user.id,
            loan_id=loan.id,
            prompt_type="settlement_letter",
            prompt=prompt,
            response=response_text
        )
        db.add(history)
        db.commit()
        db.refresh(history)

        return {
            "loan_id": loan.id,
            "letter_content": response_text
        }

    @staticmethod
    def generate_negotiation_email(db: Session, user: User, request_in: NegotiationRequest, api_key: str = None) -> dict:
        """
        Coordinates generating a professional email proposal to the creditor requesting debt settlement.
        """
        loan = LoanService.get_loan(db, request_in.loan_id, user.id)
        analysis = FinancialAnalysisService.calculate_analysis(db, user)
        recs = SettlementService.generate_recommendations(db, user)
        
        target_rec = next((r for r in recs if r.loan_id == loan.id), None)
        if not target_rec:
            raise FinReliefException(
                message="Settlement recommendation not found for this loan.",
                code="RECOMMENDATION_NOT_FOUND",
                status_code=404
            )

        hardship = request_in.custom_hardship_description or "Borrower is experiencing severe financial hardship and cash surplus constraints making full repayment unfeasible."
        
        prompt = NEGOTIATION_EMAIL_PROMPT.format(
            lender_name=loan.lender_name,
            loan_type=loan.loan_type,
            outstanding_amount=loan.outstanding_amount,
            recommended_amount=target_rec.recommended_amount,
            settlement_percentage=target_rec.settlement_percentage,
            hardship_description=hardship,
            name=user.name
        )

        response_text = GeminiClient.generate_content_with_retry(prompt, api_key=api_key)

        # Parse subject line from standard email template formatting
        subject = "Settlement Proposal Offer"
        body = response_text
        if "Subject:" in response_text:
            parts = response_text.split("---", 1)
            subject_part = parts[0]
            body_part = parts[1] if len(parts) > 1 else parts[0]
            subject = subject_part.replace("Subject:", "").strip()
            body = body_part.strip()

        history = AIHistory(
            user_id=user.id,
            loan_id=loan.id,
            prompt_type="negotiation_email",
            prompt=prompt,
            response=response_text
        )
        db.add(history)
        db.commit()
        db.refresh(history)

        return {
            "loan_id": loan.id,
            "subject": subject,
            "email_body": body
        }

    @staticmethod
    def explain_financial_analysis(db: Session, user: User, api_key: str = None) -> dict:
        """
        Coordinates generating a supportive plain-English interpretation explanation of user health analysis stats.
        """
        analysis = FinancialAnalysisService.calculate_analysis(db, user)
        recs_str = "\n".join(f"- {r}" for r in analysis["recommendations"])

        prompt = FINANCIAL_EXPLANATION_PROMPT.format(
            monthly_income=analysis["monthly_income"],
            monthly_expenses=analysis["monthly_expenses"],
            monthly_surplus=analysis["monthly_surplus"],
            dti_ratio=analysis["dti_ratio"],
            emi_ratio=analysis["emi_ratio"],
            financial_health_score=analysis["financial_health_score"],
            risk_level=analysis["risk_level"],
            repayment_capacity=analysis["repayment_capacity"],
            recommendations=recs_str
        )

        response_text = GeminiClient.generate_content_with_retry(prompt, api_key=api_key)

        history = AIHistory(
            user_id=user.id,
            loan_id=None,
            prompt_type="financial_explanation",
            prompt=prompt,
            response=response_text
        )
        db.add(history)
        db.commit()
        db.refresh(history)

        return {
            "explanation": response_text
        }

    @staticmethod
    def get_history(db: Session, user: User) -> List[AIHistory]:
        """
        Retrieves all AI history log records registered under the authenticated user.
        """
        return db.query(AIHistory).filter(AIHistory.user_id == user.id).all()

    @staticmethod
    def get_history_by_id(db: Session, history_id: int, user: User) -> AIHistory:
        """
        Fetches a specific history log record. Validates ownership blocks first.
        """
        history = db.query(AIHistory).filter(AIHistory.id == history_id).first()
        if not history:
            raise FinReliefException(
                message="AI History record not found.",
                code="HISTORY_NOT_FOUND",
                status_code=404
            )
            
        if history.user_id != user.id:
            raise FinReliefException(
                message="You do not have permission to access this history record.",
                code="FORBIDDEN",
                status_code=403
            )
            
        return history
