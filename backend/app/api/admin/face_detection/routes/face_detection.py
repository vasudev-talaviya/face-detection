from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.api.admin.face_detection.dependencies import get_detection_service
from app.api.admin.face_detection.schemas.face_detection import FaceDetectionRequest
from app.core.base import APIResponse
from app.core.logging import get_logger
from app.api.admin.face_detection.services.detection import DetectionService

logger = get_logger(__name__)

router = APIRouter(prefix="/faces", tags=["Face Detection"])


@router.post("/detect", summary="Detect and recognize faces")
def detect_and_recognize_faces(
    request: FaceDetectionRequest,
    service: DetectionService = Depends(get_detection_service),
):
    try:
        return service.detect_faces(request.image)
    except Exception as exc:
        from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure

        if isinstance(exc, (ServerSelectionTimeoutError, ConnectionFailure, OSError)):
            logger.warning("MongoDB unavailable during face detection: %s", exc)
            return JSONResponse(
                status_code=503,
                content=APIResponse.error(
                    message="Database is not available. Please ensure MongoDB is running.",
                    error_code="DATABASE_UNAVAILABLE",
                ),
            )
        raise
