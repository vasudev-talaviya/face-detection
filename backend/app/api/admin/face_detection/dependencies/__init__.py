from functools import lru_cache

from app.core.config import get_settings
from app.api.admin.users.dependencies import get_user_repository
from app.api.admin.attendance.dependencies import get_attendance_repository
from app.api.admin.face_detection.services.detection import DetectionService


@lru_cache
def get_detection_service() -> DetectionService:
    return DetectionService(
        get_user_repository(),
        get_attendance_repository(),
        get_settings().max_image_bytes,
    )
