from fastapi import APIRouter

from app.core.base import APIResponse
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["Health"])


@router.get("/health", summary="Get API health status")
def get_health_status() -> dict:
    """Health check that also reports MongoDB connectivity."""
    db_status = "unknown"
    try:
        from app.db.mongo import get_mongo_client

        client = get_mongo_client()
        client.admin.command("ping")
        db_status = "connected"
    except Exception as exc:
        logger.warning("MongoDB health check failed: %s", exc)
        db_status = "disconnected"

    return APIResponse.success(
        message="API is healthy and running",
        database=db_status,
    )
