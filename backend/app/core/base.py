"""Base classes for services and repositories following DRY principle."""

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class BaseRepository(ABC):
    """Abstract base class for all repositories."""

    @abstractmethod
    def get_by_id(self, id: str) -> Any:
        """Retrieve entity by ID."""
        pass

    @abstractmethod
    def get_all(self) -> list[Any]:
        """Retrieve all entities."""
        pass

    @abstractmethod
    def create(self, data: dict) -> Any:
        """Create new entity."""
        pass

    @abstractmethod
    def update(self, id: str, data: dict) -> Any:
        """Update existing entity."""
        pass

    @abstractmethod
    def delete(self, id: str) -> bool:
        """Delete entity by ID."""
        pass


class BaseService(ABC):
    """Abstract base class for all services with common patterns."""

    def __init__(self, repository: BaseRepository) -> None:
        self.repository = repository


class APIResponse:
    """Centralized API response builder to ensure consistent response format."""

    @staticmethod
    def success(data: Any = None, message: str = "Success", **kwargs) -> dict:
        """Build a success response."""
        response = {
            "success": True,
            "message": message,
        }
        if data is not None:
            response["data"] = data
        response.update(kwargs)
        return response

    @staticmethod
    def error(message: str, error_code: str | None = None, **kwargs) -> dict:
        """Build an error response."""
        response = {
            "success": False,
            "message": message,
        }
        if error_code:
            response["error_code"] = error_code
        response.update(kwargs)
        return response

    @staticmethod
    def paginated(
        items: list,
        total: int,
        page: int = 1,
        page_size: int = 10,
        **kwargs,
    ) -> dict:
        """Build a paginated response."""
        return {
            "success": True,
            "data": items,
            "pagination": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "pages": (total + page_size - 1) // page_size,
            },
            **kwargs,
        }
