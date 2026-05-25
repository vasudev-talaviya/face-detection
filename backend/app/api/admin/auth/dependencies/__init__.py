from functools import lru_cache
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import get_settings
from app.api.admin.auth.repositories import AuthRepository
from app.api.admin.auth.services import AuthService
from app.api.admin.auth.utils import decode_token

security = HTTPBearer()


@lru_cache
def get_auth_repository() -> AuthRepository:
    return AuthRepository()


@lru_cache
def get_auth_service() -> AuthService:
    return AuthService(get_auth_repository())


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    settings = get_settings()
    secret_key = settings.api_key or "default_secret_key"
    token = credentials.credentials
    payload = decode_token(token, secret_key)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token or expired token",
        )
    return payload


def verify_admin_role(user: dict = Depends(get_current_user)) -> dict:
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return user
