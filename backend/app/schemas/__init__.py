from app.schemas.user import UserBase, UserCreate, UserUpdate, UserResponse
from app.schemas.financial_profile import (
    FinancialProfileBase,
    FinancialProfileCreate,
    FinancialProfileUpdate,
    FinancialProfileResponse
)
from app.schemas.loan import LoanBase, LoanCreate, LoanUpdate, LoanResponse
from app.schemas.settlement_prediction import (
    SettlementPredictionBase,
    SettlementPredictionCreate,
    SettlementPredictionUpdate,
    SettlementPredictionResponse
)
from app.schemas.ai_history import (
    AIHistoryBase,
    AIHistoryCreate,
    AIHistoryUpdate,
    AIHistoryResponse
)
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.schemas.document import DocumentResponse
from app.schemas.admin import AdminLoginRequest, AdminTokenResponse, AdminDashboardMetrics

__all__ = [
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "FinancialProfileBase",
    "FinancialProfileCreate",
    "FinancialProfileUpdate",
    "FinancialProfileResponse",
    "LoanBase",
    "LoanCreate",
    "LoanUpdate",
    "LoanResponse",
    "SettlementPredictionBase",
    "SettlementPredictionCreate",
    "SettlementPredictionUpdate",
    "SettlementPredictionResponse",
    "AIHistoryBase",
    "AIHistoryCreate",
    "AIHistoryUpdate",
    "AIHistoryResponse",
    "RegisterRequest",
    "LoginRequest",
    "TokenResponse",
    "DocumentResponse",
    "AdminLoginRequest",
    "AdminTokenResponse",
    "AdminDashboardMetrics",
]
