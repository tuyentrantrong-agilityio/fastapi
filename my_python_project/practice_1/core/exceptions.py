"""
Custom exceptions for the application.

These exceptions provide a standardized way to handle errors
and can be converted to HTTP responses via global exception handlers.
"""

from typing import Optional


class ApplicationException(Exception):
    """
    Base exception class for all application exceptions.

    Attributes:
        message: Human-readable error message
        status_code: HTTP status code
        detail: Detailed error information (optional)
    """

    def __init__(self, message: str, status_code: int, detail: Optional[str] = None):
        """
        Initialize ApplicationException.

        Args:
            message: Human-readable error message
            status_code: HTTP status code
            detail: Optional detailed error information
        """
        self.message = message
        self.status_code = status_code
        self.detail = detail or message
        super().__init__(self.detail)


class NotFoundException(ApplicationException):
    """
    Raised when a requested resource is not found.

    HTTP Status: 404 Not Found
    """

    def __init__(self, resource: str, resource_id: Optional[int] = None):
        """
        Initialize NotFoundException.

        Args:
            resource: Name of the resource (e.g., "Task", "Project", "User")
            resource_id: Optional ID of the resource for context
        """
        if resource_id:
            message = f"{resource} {resource_id} not found"
        else:
            message = f"{resource} not found"
        super().__init__(message, status_code=404, detail=message)


class ForbiddenException(ApplicationException):
    """
    Raised when user lacks permission to access a resource.

    HTTP Status: 403 Forbidden
    """

    def __init__(
        self, detail: str = "You don't have permission to access this resource"
    ):
        """
        Initialize ForbiddenException.

        Args:
            detail: Detailed error message explaining why access is forbidden
        """
        super().__init__(detail, status_code=403, detail=detail)


class UnauthorizedException(ApplicationException):
    """
    Raised when authentication is required but not provided or invalid.

    HTTP Status: 401 Unauthorized
    """

    def __init__(self, detail: str = "Invalid or missing authentication credentials"):
        """
        Initialize UnauthorizedException.

        Args:
            detail: Detailed error message explaining authentication failure
        """
        super().__init__(detail, status_code=401, detail=detail)


class BadRequestException(ApplicationException):
    """
    Raised when request contains invalid data.

    HTTP Status: 400 Bad Request
    """

    def __init__(self, detail: str):
        """
        Initialize BadRequestException.

        Args:
            detail: Detailed error message about what's invalid in the request
        """
        super().__init__(detail, status_code=400, detail=detail)


class ConflictException(ApplicationException):
    """
    Raised when request conflicts with existing data.

    HTTP Status: 409 Conflict
    """

    def __init__(self, detail: str):
        """
        Initialize ConflictException.

        Args:
            detail: Detailed error message explaining the conflict
        """
        super().__init__(detail, status_code=409, detail=detail)
