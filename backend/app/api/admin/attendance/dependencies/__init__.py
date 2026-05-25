from functools import lru_cache

from app.api.admin.attendance.repositories.attendance import AttendanceRepository
from app.api.admin.attendance.services.attendance import AttendanceService


@lru_cache
def get_attendance_repository() -> AttendanceRepository:
    return AttendanceRepository()


@lru_cache
def get_attendance_service() -> AttendanceService:
    return AttendanceService(get_attendance_repository())
