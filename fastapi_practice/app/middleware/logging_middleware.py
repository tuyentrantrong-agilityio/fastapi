"""Logging middleware for request/response tracking."""

import logging
import time
import uuid
from typing import Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all incoming requests and outgoing responses"""

    def __init__(self, app):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())
        start_time = time.time()

        logger.info(
            f"--> Request: {request.method} {request.url.path}",
            extra={"request_id": request_id, "method": request.method, "path": request.url.path},
        )

        try:
            response = await call_next(request)
            process_time = time.time() - start_time

            logger.info(
                f"<-- Response: {request.method} {request.url.path} - {response.status_code} ({process_time:.3f}s)",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_seconds": float(process_time),
                },
            )

            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)

            return response
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"<-- Error: {request.method} {request.url.path} - Exception: {str(e)}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "error": str(e),
                    "duration_seconds": float(process_time),
                },
                exc_info=True,
            )
            raise
