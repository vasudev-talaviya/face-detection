import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


def _csv_env(name: str, default: str) -> tuple[str, ...]:
    value = os.getenv(name, default)
    return tuple(item.strip() for item in value.split(",") if item.strip())


def _bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


def _positive_int_env(name: str, default: int) -> int:
    try:
        value = int(os.getenv(name, str(default)))
    except ValueError:
        return default
    return value if value > 0 else default


@dataclass(frozen=True)
class Settings:
    app_name: str
    app_version: str
    docs_enabled: bool
    mongodb_url: str
    mongodb_database_name: str
    cors_origins: tuple[str, ...]
    trusted_hosts: tuple[str, ...]
    max_request_bytes: int
    max_image_bytes: int
    api_key: str | None


@lru_cache
def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "Face Detection & Registration API"),
        app_version=os.getenv("APP_VERSION", "1.0.0"),
        docs_enabled=_bool_env("API_DOCS_ENABLED", True),
        mongodb_url=os.getenv("MONGODB_URL", "mongodb://localhost:27017/"),
        mongodb_database_name=os.getenv("MONGODB_DATABASE_NAME", "face_detection"),
        cors_origins=_csv_env(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        ),
        trusted_hosts=_csv_env("TRUSTED_HOSTS", "*"),
        max_request_bytes=_positive_int_env("MAX_REQUEST_BYTES", 15 * 1024 * 1024),
        max_image_bytes=_positive_int_env("MAX_IMAGE_BYTES", 10 * 1024 * 1024),
        api_key=os.getenv("API_KEY") or None,
    )
