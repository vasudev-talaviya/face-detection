from dataclasses import dataclass

from bson import ObjectId
from bson.errors import InvalidId

from app.core.base import BaseRepository
from app.core.logging import get_logger
from app.api.admin.users.models.users import UserDocument
from app.db.mongo import get_database
from app.ml.similarity import ml_face_embedding_check_with_id

logger = get_logger(__name__)


@dataclass(frozen=True)
class FaceMatch:
    """Data class for face matching results."""

    is_new_face: bool
    matched_name: str | None
    confidence: float
    user_id: str | None = None


class UserRepository(BaseRepository):
    """Persistence and matching operations for registered users."""

    def __init__(self, database=None) -> None:
        database = database if database is not None else get_database()
        self.collection = database["ImageEmbedding"]
        logger.info("UserRepository initialized")

    # Abstract method implementations
    def get_by_id(self, id: str) -> dict | None:
        """Retrieve user by ID."""
        try:
            object_id = ObjectId(id)
            return self.collection.find_one({"_id": object_id})
        except InvalidId as e:
            logger.warning(f"Invalid user ID format: {id}")
            return None

    def get_all(self) -> list[dict]:
        """Retrieve all users - alias for list_users."""
        return self.list_users()

    def create(self, data: dict) -> str | None:
        """Create new user."""
        try:
            name = data.get("name")
            embedding = data.get("embedding", [])
            success, _, _ = self.save_embedding(name, embedding[0] if embedding else [])
            return data.get("_id") if success else None
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None

    def update(self, id: str, data: dict, embedding: list[float] | None = None) -> bool:
        """Update user by ID and optionally add an embedding."""
        try:
            object_id = ObjectId(id)
            update_op = {"$set": data}
            if embedding:
                update_op["$addToSet"] = {"embedding": embedding}
            result = self.collection.update_one({"_id": object_id}, update_op)
            return result.modified_count > 0
        except InvalidId as e:
            logger.warning(f"Invalid user ID format: {id}")
            return False

    def delete(self, id: str) -> bool:
        """Delete user by ID - alias for delete_user."""
        return self.delete_user(id)

    # Core repository methods
    def face_records(self) -> list[dict]:
        """Retrieve all user face records with embeddings."""
        return list(self.collection.find({}, {"embedding": 1, "name": 1, "_id": 1}))

    def match_embeddings(
        self,
        embeddings: list[list[float]],
        records: list[dict] | None = None,
    ) -> FaceMatch:
        is_new, name, confidence, user_id = ml_face_embedding_check_with_id(
            records if records is not None else self.face_records(),
            embeddings,
        )
        return FaceMatch(is_new, name, confidence, user_id)

    def match_embedding(self, embedding: list[float], records: list[dict] | None = None) -> FaceMatch:
        return self.match_embeddings([embedding], records)

    def create_user(self, name: str, embeddings: list[list[float]]) -> bool:
        validated = UserDocument(name=name, embedding=embeddings)
        result = self.collection.insert_one(validated.model_dump(mode="json"))
        return bool(result.inserted_id)

    def save_embedding(self, name: str, embedding: list[float]) -> tuple[bool, bool, bool]:
        validated = UserDocument(name=name, embedding=[embedding])
        existing = self.collection.find_one({"name": validated.name}, {"_id": 1})
        if existing:
            result = self.collection.update_one(
                {"_id": existing["_id"]},
                {"$addToSet": {"embedding": validated.embedding[0]}},
            )
            return result.acknowledged, True, result.modified_count > 0
        result = self.collection.insert_one(validated.model_dump(mode="json"))
        return bool(result.inserted_id), False, True

    def list_users(self) -> list[dict]:
        users = []
        for document in self.collection.find({}, {"name": 1, "embedding": 1}):
            embeddings = document.get("embedding", [])
            users.append(
                {
                    "id": str(document["_id"]),
                    "name": document.get("name", "Unknown"),
                    "template_count": len(embeddings) if isinstance(embeddings, list) else 1,
                }
            )
        return users

    def delete_user(self, user_id: str) -> bool:
        try:
            object_id = ObjectId(user_id)
        except InvalidId as exc:
            raise ValueError("Invalid ObjectId.") from exc
        return self.collection.delete_one({"_id": object_id}).deleted_count > 0
