from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.orm import Session
from typing import Optional, List
from app.dependencies.db import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.ai import (
    NegotiationRequest,
    NegotiationResponse,
    SettlementLetterResponse,
    NegotiationEmailResponse,
    FinancialExplanationResponse,
    AIHistoryResponse
)
from app.services.ai_service import AIService
from app.utils.response_utils import success_response

ai_router = APIRouter()

@ai_router.post(
    "/negotiation-strategy",
    summary="Generate Negotiation Strategy Guide",
    response_model=None
)
def generate_strategy(
    request: NegotiationRequest,
    x_gemini_key: Optional[str] = Header(None, alias="x-gemini-api-key"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Computes a tailored professional guide of steps and concerns for creditor negotiations.
    """
    data = AIService.generate_negotiation_strategy(
        db=db,
        user=current_user,
        request_in=request,
        api_key=x_gemini_key
    )
    return success_response(
        data=NegotiationResponse.model_validate(data),
        message="Negotiation strategy generated successfully.",
        status_code=status.HTTP_200_OK
    )

@ai_router.post(
    "/settlement-letter",
    summary="Generate Settlement Request Proposal Letter",
    response_model=None
)
def generate_letter(
    request: NegotiationRequest,
    x_gemini_key: Optional[str] = Header(None, alias="x-gemini-api-key"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generates a formal proposal letter requesting settlement in business layout.
    """
    data = AIService.generate_settlement_letter(
        db=db,
        user=current_user,
        request_in=request,
        api_key=x_gemini_key
    )
    return success_response(
        data=SettlementLetterResponse.model_validate(data),
        message="Settlement letter generated successfully.",
        status_code=status.HTTP_200_OK
    )

@ai_router.post(
    "/negotiation-email",
    summary="Generate Creditor Proposal Email",
    response_model=None
)
def generate_email(
    request: NegotiationRequest,
    x_gemini_key: Optional[str] = Header(None, alias="x-gemini-api-key"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generates a concise proposal email requesting settlement compromise.
    """
    data = AIService.generate_negotiation_email(
        db=db,
        user=current_user,
        request_in=request,
        api_key=x_gemini_key
    )
    return success_response(
        data=NegotiationEmailResponse.model_validate(data),
        message="Negotiation email generated successfully.",
        status_code=status.HTTP_200_OK
    )

@ai_router.post(
    "/financial-explanation",
    summary="Generate plain-English Analysis explanation",
    response_model=None
)
def generate_explanation(
    x_gemini_key: Optional[str] = Header(None, alias="x-gemini-api-key"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Interprets user health scores and repayment limits into a supportive explanation.
    """
    data = AIService.explain_financial_analysis(
        db=db,
        user=current_user,
        api_key=x_gemini_key
    )
    return success_response(
        data=FinancialExplanationResponse.model_validate(data),
        message="Financial explanation generated successfully.",
        status_code=status.HTTP_200_OK
    )

@ai_router.get(
    "/history",
    summary="Get AI Generation History Logs",
    response_model=None
)
def get_history_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves all AI history log entries logged by the active user session.
    """
    logs = AIService.get_history(db=db, user=current_user)
    serialized = [AIHistoryResponse.model_validate(log) for log in logs]
    return success_response(
        data=serialized,
        message="AI history logs retrieved successfully.",
        status_code=status.HTTP_200_OK
    )

@ai_router.get(
    "/history/{history_id}",
    summary="Get Specific AI Generation History Log",
    response_model=None
)
def get_history_log(
    history_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves details of a single logged AI interaction. Enforces ownership locks.
    """
    log = AIService.get_history_by_id(db=db, history_id=history_id, user=current_user)
    return success_response(
        data=AIHistoryResponse.model_validate(log),
        message="AI history log retrieved successfully.",
        status_code=status.HTTP_200_OK
    )
