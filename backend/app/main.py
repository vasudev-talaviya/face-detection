from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.admin.router import router as admin_router
from app.api.admin.health.routes import router as health_router
from app.core.config import get_settings
from app.core.exceptions import configure_exception_handlers
from app.core.logging import get_logger
from app.core.security import configure_security
from app.db.mongo import close_mongo_client
from app.middleware import RequestLoggingMiddleware

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Handle application startup and shutdown."""
    logger.info("Application startup")
    yield
    logger.info("Application shutdown")
    close_mongo_client()


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    logger.info("Creating FastAPI application")
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url="/docs" if settings.docs_enabled else None,
        redoc_url="/redoc" if settings.docs_enabled else None,
        lifespan=lifespan,
    )

    # Configure security and exception handling
    configure_security(app, settings)
    configure_exception_handlers(app)

    # Add middleware
    app.add_middleware(RequestLoggingMiddleware)

    # Include routers
    app.include_router(health_router, prefix="/api")
    app.include_router(admin_router, prefix="/api/admin")

    logger.info(f"FastAPI application configured: {settings.app_name} v{settings.app_version}")
    return app


app = create_app()
