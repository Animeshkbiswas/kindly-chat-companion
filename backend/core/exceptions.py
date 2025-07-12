"""
Custom exceptions for the therapy chat application
Provides specific error handling for different scenarios.
"""

from typing import Optional
from fastapi import HTTPException, status


class TherapyChatException(Exception):
    """Base exception for therapy chat application"""
    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class UserNotFoundException(TherapyChatException):
    """Raised when user is not found"""
    def __init__(self, user_id: int):
        super().__init__(f"User with id {user_id} not found", "USER_NOT_FOUND")


class SessionNotFoundException(TherapyChatException):
    """Raised when therapy session is not found"""
    def __init__(self, session_id: int):
        super().__init__(f"Session with id {session_id} not found", "SESSION_NOT_FOUND")


class InvalidCredentialsException(TherapyChatException):
    """Raised when authentication credentials are invalid"""
    def __init__(self):
        super().__init__("Invalid username or password", "INVALID_CREDENTIALS")


class AIServiceException(TherapyChatException):
    """Raised when AI service encounters an error"""
    def __init__(self, service: str, error: str):
        super().__init__(f"AI service {service} error: {error}", "AI_SERVICE_ERROR")


class AudioProcessingException(TherapyChatException):
    """Raised when audio processing fails"""
    def __init__(self, operation: str, error: str):
        super().__init__(f"Audio {operation} failed: {error}", "AUDIO_PROCESSING_ERROR")


class ReportGenerationException(TherapyChatException):
    """Raised when report generation fails"""
    def __init__(self, report_type: str, error: str):
        super().__init__(f"Report generation ({report_type}) failed: {error}", "REPORT_GENERATION_ERROR")


class ValidationException(TherapyChatException):
    """Raised when data validation fails"""
    def __init__(self, field: str, value: str):
        super().__init__(f"Validation failed for {field}: {value}", "VALIDATION_ERROR")


# HTTP Exception helpers
def create_http_exception(
    status_code: int,
    detail: str,
    error_code: Optional[str] = None
) -> HTTPException:
    """Create HTTPException with optional error code"""
    return HTTPException(
        status_code=status_code,
        detail={"message": detail, "error_code": error_code} if error_code else detail
    )


def user_not_found_exception(user_id: int) -> HTTPException:
    """HTTP exception for user not found"""
    return create_http_exception(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"User with id {user_id} not found",
        error_code="USER_NOT_FOUND"
    )


def session_not_found_exception(session_id: int) -> HTTPException:
    """HTTP exception for session not found"""
    return create_http_exception(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Session with id {session_id} not found",
        error_code="SESSION_NOT_FOUND"
    )


def invalid_credentials_exception() -> HTTPException:
    """HTTP exception for invalid credentials"""
    return create_http_exception(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
        error_code="INVALID_CREDENTIALS"
    )


def ai_service_exception(service: str, error: str) -> HTTPException:
    """HTTP exception for AI service errors"""
    return create_http_exception(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=f"AI service {service} is currently unavailable: {error}",
        error_code="AI_SERVICE_ERROR"
    )


def audio_processing_exception(operation: str, error: str) -> HTTPException:
    """HTTP exception for audio processing errors"""
    return create_http_exception(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=f"Audio {operation} failed: {error}",
        error_code="AUDIO_PROCESSING_ERROR"
    )


def validation_exception(field: str, value: str) -> HTTPException:
    """HTTP exception for validation errors"""
    return create_http_exception(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Validation failed for {field}: {value}",
        error_code="VALIDATION_ERROR"
    )