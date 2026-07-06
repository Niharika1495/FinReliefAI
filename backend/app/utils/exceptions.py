from app.utils.constants import (
    ERR_INTERNAL_SERVER_ERROR,
    ERR_ENTITY_NOT_FOUND,
    ERR_VALIDATION_FAILED,
    ERR_UNAUTHORIZED_ACCESS,
    ERR_FORBIDDEN_ACCESS
)

class FinReliefException(Exception):
    """
    Base exception class for the FinRelief AI platform.
    Allows passing customized API error codes and HTTP status codes.
    """
    def __init__(self, message: str, code: str = ERR_INTERNAL_SERVER_ERROR, status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code

class EntityNotFoundException(FinReliefException):
    """
    Exception raised when a requested resource (e.g., User, Loan)
    is missing in the persistence layer.
    """
    def __init__(self, message: str = "Requested resource not found"):
        super().__init__(message, code=ERR_ENTITY_NOT_FOUND, status_code=404)

class ValidationException(FinReliefException):
    """
    Exception raised when business validations fail.
    """
    def __init__(self, message: str = "Request data validation failed"):
        super().__init__(message, code=ERR_VALIDATION_FAILED, status_code=422)

class UnauthorizedException(FinReliefException):
    """
    Exception raised when authorization token parsing or validation fails.
    """
    def __init__(self, message: str = "Authentication credentials required"):
        super().__init__(message, code=ERR_UNAUTHORIZED_ACCESS, status_code=401)

class ForbiddenException(FinReliefException):
    """
    Exception raised when authorized users attempt actions beyond their roles.
    """
    def __init__(self, message: str = "Action forbidden for current user role"):
        super().__init__(message, code=ERR_FORBIDDEN_ACCESS, status_code=403)
