from fastapi import APIRouter

from app.api.admin.auth.routes import router as auth_router
from app.api.admin.users.routes import router as users_router
from app.api.admin.attendance.routes import router as attendance_router
from app.api.admin.face_detection.routes import router as faces_router
from app.api.admin.health.routes import router as health_router

router = APIRouter()

# Register all modular sub-routers
router.include_router(auth_router)
router.include_router(users_router)
router.include_router(attendance_router)
router.include_router(faces_router)
router.include_router(health_router)
