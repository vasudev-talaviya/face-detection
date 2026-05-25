from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from app.api.admin.users.dependencies import get_user_service
from app.api.admin.face_detection.dependencies import get_detection_service
from app.api.admin.users.schemas.users import RegisterUserRequest, UpdateUserRequest
from app.core.base import APIResponse
from app.core.logging import get_logger
from app.api.admin.users.services.users import UserService
from app.api.admin.face_detection.services.detection import DetectionService

logger = get_logger(__name__)

router = APIRouter(prefix="/users", tags=["Users"])


def _db_error_response(operation: str, exc: Exception):
    """Return a 503 JSONResponse for database errors, or re-raise."""
    from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure

    if isinstance(exc, (ServerSelectionTimeoutError, ConnectionFailure, OSError)):
        logger.warning("MongoDB unavailable during %s: %s", operation, exc)
        return JSONResponse(
            status_code=503,
            content=APIResponse.error(
                message="Database is not available. Please ensure MongoDB is running.",
                error_code="DATABASE_UNAVAILABLE",
            ),
        )
    raise exc


@router.post("", summary="Register a user face template")
def register_user(
    request: RegisterUserRequest,
    user_service: UserService = Depends(get_user_service),
    detection_service: DetectionService = Depends(get_detection_service),
):
    try:
        _, _, embeddings, _ = detection_service._analyse(request.image)
        if len(embeddings) == 0:
            raise HTTPException(status_code=400, detail="No face detected in the provided image.")
        if len(embeddings) > 1:
            raise HTTPException(status_code=400, detail="Multiple faces detected. Please provide an image with a single face.")
            
        return user_service.register(request.name, embeddings[0])
    except HTTPException:
        raise
    except Exception as exc:
        return _db_error_response("register_user", exc)


@router.get("", summary="List registered users")
def list_users(service: UserService = Depends(get_user_service)):
    try:
        return service.list_users()
    except Exception as exc:
        return _db_error_response("list_users", exc)


@router.delete("/{user_id}", summary="Delete a registered user")
def delete_user(user_id: str, service: UserService = Depends(get_user_service)):
    try:
        return service.delete_user(user_id)
    except Exception as exc:
        return _db_error_response("delete_user", exc)


@router.put("/{user_id}", summary="Update a registered user")
def update_user(
    user_id: str, 
    request: UpdateUserRequest, 
    service: UserService = Depends(get_user_service),
    detection_service: DetectionService = Depends(get_detection_service),
):
    try:
        embedding = None
        if request.image:
            _, _, embeddings, _ = detection_service._analyse(request.image)
            if len(embeddings) == 0:
                raise HTTPException(status_code=400, detail="No face detected in the provided image.")
            if len(embeddings) > 1:
                raise HTTPException(status_code=400, detail="Multiple faces detected.")
            embedding = embeddings[0]
            
        return service.update_user(user_id, request.name, embedding)
    except HTTPException:
        raise
    except Exception as exc:
        return _db_error_response("update_user", exc)
