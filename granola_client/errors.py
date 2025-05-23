from typing import Any


class GranolaAPIError(Exception):
    """Base exception for Granola API errors."""
    def __init__(self, message: str, status_code: int | None = None, response_text: str | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text

    def __str__(self):
        if self.status_code:
            return f"HTTP {self.status_code}: {super().__str__()} - {self.response_text or ''}"
        return super().__str__()

class GranolaAuthError(GranolaAPIError):
    """Exception for authentication-related errors."""
    def __init__(self, message: str = "Authentication failed or token could not be retrieved."):
        super().__init__(message)

class GranolaRateLimitError(GranolaAPIError):
    """Exception for rate limit errors (HTTP 429)."""
    def __init__(self, message: str, status_code: int = 429, response_text: str | None = None, retry_after: int | None = None):
        super().__init__(message, status_code, response_text)
        self.retry_after = retry_after # seconds

class GranolaTimeoutError(GranolaAPIError):
    """Exception for request timeouts."""
    def __init__(self, message: str = "Request timed out."):
        super().__init__(message)

class GranolaValidationError(GranolaAPIError):
    """Exception for Pydantic validation errors on API responses."""
    def __init__(self, message: str, validation_errors: Any = None, response_text: str | None = None):
        super().__init__(f"Response validation failed: {message}")
        self.validation_errors = validation_errors
        self.response_text = response_text

    def __str__(self):
        return f"{super().__str__()} (Details: {self.validation_errors})"
