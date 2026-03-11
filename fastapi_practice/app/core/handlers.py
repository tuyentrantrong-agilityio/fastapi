"""
Global exception handlers for standardized error responses.

This module provides centralized error handling for the FastAPI application,
ensuring consistent error response formats across all endpoints.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from .exceptions import ApplicationException
import logging

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI):
    """
    Register all global exception handlers with the FastAPI app.

    This function should be called during application startup to register
    handlers for custom and standard exceptions.

    Args:
        app: FastAPI application instance
    """

    @app.exception_handler(ApplicationException)
    async def application_exception_handler(
        request: Request, exc: ApplicationException
    ):
        """
        Handle custom ApplicationException and its subclasses.

        Converts custom exceptions to standardized JSON error responses.

        Args:
            request: The incoming HTTP request
            exc: The ApplicationException that was raised

        Returns:
            JSONResponse with error details and appropriate HTTP status code
        """
        logger.warning(
            f"Application exception: {exc.message}",
            extra={
                "status_code": exc.status_code,
                "detail": exc.detail,
                "path": request.url.path,
            },
        )

        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "message": exc.message,
                    "detail": exc.detail,
                    "status_code": exc.status_code,
                },
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """
        Handle HTTPException (e.g., from OAuth2PasswordBearer authentication).

        Converts HTTPException to standardized JSON error response format.
        This catches "Not authenticated" errors from OAuth2PasswordBearer.

        Args:
            request: The incoming HTTP request
            exc: The HTTPException that was raised

        Returns:
            JSONResponse with error details in standardized format
        """
        # Convert "Not authenticated" to our standard format
        if exc.status_code == 403 and "Not authenticated" in str(exc.detail):
            status_code = 401
            message = "Unauthorized"
            detail = "Missing or invalid authentication credentials"
        else:
            status_code = exc.status_code
            message = exc.detail
            detail = exc.detail

        logger.warning(
            f"HTTP exception: {message}",
            extra={
                "status_code": status_code,
                "detail": detail,
                "path": request.url.path,
            },
        )

        return JSONResponse(
            status_code=status_code,
            content={
                "error": {
                    "message": message,
                    "detail": detail,
                    "status_code": status_code,
                },
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """
        Handle unexpected exceptions.

        This is a catch-all handler for any exception not explicitly handled.
        It logs the error and returns a generic 500 error response.

        Args:
            request: The incoming HTTP request
            exc: The exception that was raised

        Returns:
            JSONResponse with generic error message and 500 status code
        """
        logger.error(
            f"Unexpected exception: {str(exc)}",
            exc_info=exc,
            extra={"path": request.url.path},
        )

        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "message": "Internal Server Error",
                    "detail": "An unexpected error occurred. Please try again later.",
                    "status_code": 500,
                },
            },
        )
