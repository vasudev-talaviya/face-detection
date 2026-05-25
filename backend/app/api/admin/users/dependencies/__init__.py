from functools import lru_cache

from app.api.admin.users.repositories.users import UserRepository
from app.api.admin.users.services.users import UserService


@lru_cache
def get_user_repository() -> UserRepository:
    return UserRepository()


@lru_cache
def get_user_service() -> UserService:
    return UserService(get_user_repository())
