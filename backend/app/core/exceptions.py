import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.base import APIResponse
from app.core.logging import get_logger

logger = get_logger(__name__)


class APIError(Exception):
    """Base exception for all API errors."""

    status_code = 500
    error_code = "INTERNAL_SERVER_ERROR"
    detail = "Internal server error."

    def __init__(self, detail: str | None = None, error_code: str | None = None) -> None:
        self.detail = detail or self.detail
        if error_code:
            self.error_code = error_code
        super().__init__(self.detail)


class BadRequestError(APIError):
    """400 Bad Request error."""

    status_code = 400
    error_code = "BAD_REQUEST"
    detail = "Invalid request."


class NotFoundError(APIError):
    """404 Not Found error."""

    status_code = 404
    error_code = "NOT_FOUND"
    detail = "Resource not found."


class UnauthorizedError(APIError):
    """401 Unauthorized error."""

    status_code = 401
    error_code = "UNAUTHORIZED"
    detail = "Unauthorized access."


class ForbiddenError(APIError):
    """403 Forbidden error."""

    status_code = 403
    error_code = "FORBIDDEN"
    detail = "Forbidden access."


class ConflictError(APIError):
    """409 Conflict error."""

    status_code = 409
    error_code = "CONFLICT"
    detail = "Resource conflict."


class DatabaseUnavailableError(APIError):
    """503 Database unavailable error."""

    status_code = 503
    error_code = "DATABASE_UNAVAILABLE"
    detail = "Database is not available. Please ensure MongoDB is running."


def configure_exception_handlers(app: FastAPI) -> None:
    """Configure exception handlers for the FastAPI application."""

    @app.exception_handler(APIError)
    async def api_error_handler(_: Request, exc: APIError) -> JSONResponse:
        """Handle APIError exceptions."""
        content = APIResponse.error(
            message=exc.detail,
            error_code=exc.error_code,
        )
        return JSONResponse(status_code=exc.status_code, content=content)

    @app.exception_handler(Exception)
    async def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle unexpected exceptions."""
        # Check for MongoDB connection errors specifically
        exc_type = type(exc).__name__
        exc_module = type(exc).__module__ or ""

        if "pymongo" in exc_module or "ServerSelectionTimeoutError" in exc_type:
            logger.warning(
                "MongoDB unavailable on %s %s: %s",
                request.method,
                request.url.path,
                str(exc),
            )
            content = APIResponse.error(
                message="Database is not available. Please ensure MongoDB is running on localhost:27017.",
                error_code="DATABASE_UNAVAILABLE",
            )
            return JSONResponse(status_code=503, content=content)

        logger.exception(
            "Unhandled error on %s %s: %s",
            request.method,
            request.url.path,
            str(exc),
            exc_info=exc,
        )
        content = APIResponse.error(
            message="Internal server error.",
            error_code="INTERNAL_SERVER_ERROR",
        )
        return JSONResponse(status_code=500, content=content)
