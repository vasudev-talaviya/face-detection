from datetime import date

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from app.api.admin.attendance.dependencies import get_attendance_service
from app.api.admin.face_detection.dependencies import get_detection_service
from app.api.admin.attendance.schemas.attendance import AttendanceSubmissionRequest
from app.api.admin.face_detection.schemas.face_detection import FaceDetectionRequest
from app.core.base import APIResponse
from app.core.logging import get_logger
from app.api.admin.attendance.services.attendance import AttendanceService
from app.api.admin.face_detection.services.detection import DetectionService

logger = get_logger(__name__)

router = APIRouter(prefix="/attendance", tags=["Attendance"])


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


@router.post("/scan", summary="Scan faces for attendance")
def scan_faces_for_attendance(
    request: FaceDetectionRequest,
    service: DetectionService = Depends(get_detection_service),
):
    try:
        return service.detect_attendance_faces(request.image)
    except Exception as exc:
        return _db_error_response("scan_attendance", exc)


@router.post("", summary="Record attendance")
def record_attendance(
    request: AttendanceSubmissionRequest,
    service: AttendanceService = Depends(get_attendance_service),
):
    try:
        return service.submit(request)
    except Exception as exc:
        return _db_error_response("record_attendance", exc)


@router.get("/today", summary="Get today's attendance")
def get_today_attendance(service: AttendanceService = Depends(get_attendance_service)):
    try:
        return service.attendance_for_date(date.today())
    except Exception as exc:
        return _db_error_response("get_today_attendance", exc)


@router.get("", summary="Get attendance by date")
def get_attendance_by_date(
    attendance_date: date = Query(..., alias="date", description="Date in YYYY-MM-DD format"),
    service: AttendanceService = Depends(get_attendance_service),
):
    try:
        return service.attendance_for_date(attendance_date)
    except Exception as exc:
        return _db_error_response("get_attendance_by_date", exc)


@router.get("/corrections", summary="Get attendance corrections")
def get_attendance_corrections(service: AttendanceService = Depends(get_attendance_service)):
    try:
        return service.corrections()
    except Exception as exc:
        return _db_error_response("get_attendance_corrections", exc)


@router.get("/user/{user_id}", summary="Get attendance history for a specific user")
def get_attendance_for_user(
    user_id: str,
    service: AttendanceService = Depends(get_attendance_service)
):
    try:
        return service.attendance_for_user(user_id)
    except Exception as exc:
        return _db_error_response("get_attendance_for_user", exc)
