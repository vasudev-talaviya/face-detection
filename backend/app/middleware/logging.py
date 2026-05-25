"""Middleware for request/response logging and monitoring."""

import time
from typing import Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

from app.core.logging import get_logger

logger = get_logger(__name__)


def _is_mongo_error(exc: Exception) -> bool:
    """Check if the exception is a MongoDB connection error."""
    exc_type = type(exc).__name__
    exc_module = type(exc).__module__ or ""
    return "pymongo" in exc_module or "ServerSelectionTimeoutError" in exc_type


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all incoming requests and outgoing responses."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log request and response details."""
        # Request info
        method = request.method
        url = request.url.path
        client = request.client.host if request.client else "unknown"

        # Process request
        start_time = time.time()
        try:
            response = await call_next(request)
            process_time = time.time() - start_time

            # Log successful response
            logger.info(
                f"{method} {url} - Status: {response.status_code} - "
                f"Time: {process_time:.3f}s - Client: {client}"
            )

            return response
        except Exception as e:
            process_time = time.time() - start_time

            # Intercept MongoDB connection errors and return a clean 503
            if _is_mongo_error(e):
                logger.warning(
                    f"{method} {url} - MongoDB unavailable - "
                    f"Time: {process_time:.3f}s - Client: {client}"
                )
                return JSONResponse(
                    status_code=503,
                    content={
                        "success": False,
                        "message": "Database is not available. Please ensure MongoDB is running.",
                        "error_code": "DATABASE_UNAVAILABLE",
                    },
                )

            logger.error(
                f"{method} {url} - Error - Time: {process_time:.3f}s - Client: {client} - {str(e)}",
                exc_info=True,
            )
            raise
