from copy import deepcopy
from dataclasses import dataclass
import unittest

from bson import ObjectId

from app.api.admin.attendance.repositories.attendance import AttendanceRepository
from app.api.admin.users.repositories.users import UserRepository



@dataclass
class _InsertResult:
    inserted_id: ObjectId


@dataclass
class _UpdateResult:
    acknowledged: bool
    modified_count: int
    upserted_id: ObjectId | None = None


@dataclass
class _DeleteResult:
    deleted_count: int


class _MemoryCursor(list):
    def sort(self, field: str, direction: int):
        return _MemoryCursor(sorted(self, key=lambda document: document[field], reverse=direction < 0))


class _MemoryCollection:
    def __init__(self) -> None:
        self.documents: list[dict] = []
        self.indexes: list[tuple] = []

    @staticmethod
    def _matches(document: dict, query: dict) -> bool:
        return all(document.get(key) == value for key, value in query.items())

    @staticmethod
    def _project(document: dict, projection: dict | None) -> dict:
        if projection is None:
            return deepcopy(document)
        included_fields = {key for key, include in projection.items() if include == 1}
        if included_fields:
            return {
                key: deepcopy(value)
                for key, value in document.items()
                if (key == "_id" and projection.get("_id", 1)) or key in included_fields
            }
        result = deepcopy(document)
        for key, include in projection.items():
            if include == 0:
                result.pop(key, None)
        return result

    def insert_one(self, document: dict) -> _InsertResult:
        stored = deepcopy(document)
        stored["_id"] = ObjectId()
        self.documents.append(stored)
        return _InsertResult(stored["_id"])

    def find_one(self, query: dict, projection: dict | None = None) -> dict | None:
        for document in self.documents:
            if self._matches(document, query):
                return self._project(document, projection)
        return None

    def find(self, query: dict, projection: dict | None = None) -> _MemoryCursor:
        return _MemoryCursor([
            self._project(document, projection)
            for document in self.documents
            if self._matches(document, query)
        ])

    def update_one(self, query: dict, update: dict, upsert: bool = False) -> _UpdateResult:
        for document in self.documents:
            if self._matches(document, query):
                if "$setOnInsert" in update:
                    return _UpdateResult(True, 0)
                embedding = update["$addToSet"]["embedding"]
                if embedding in document["embedding"]:
                    return _UpdateResult(True, 0)
                document["embedding"].append(deepcopy(embedding))
                return _UpdateResult(True, 1)
        if upsert and "$setOnInsert" in update:
            result = self.insert_one(update["$setOnInsert"])
            return _UpdateResult(True, 0, result.inserted_id)
        return _UpdateResult(False, 0)

    def delete_one(self, query: dict) -> _DeleteResult:
        for index, document in enumerate(self.documents):
            if self._matches(document, query):
                del self.documents[index]
                return _DeleteResult(1)
        return _DeleteResult(0)

    def create_index(self, *keys, **options) -> None:
        self.indexes.append((keys, options))

    def count_documents(self, query: dict) -> int:
        return len([document for document in self.documents if self._matches(document, query)])


class _MemoryDatabase:
    def __init__(self) -> None:
        self.collections: dict[str, _MemoryCollection] = {}

    def __getitem__(self, collection_name: str) -> _MemoryCollection:
        return self.collections.setdefault(collection_name, _MemoryCollection())


class UserRepositoryTest(unittest.TestCase):
    def setUp(self) -> None:
        self.repository = UserRepository(_MemoryDatabase())

    def test_save_embedding_updates_existing_user_without_duplicate_templates(self) -> None:
        first_embedding = [0.1, 0.2]
        second_embedding = [0.2, 0.3]

        self.assertEqual(self.repository.save_embedding("Vasudev", first_embedding), (True, False, True))
        self.assertEqual(self.repository.save_embedding("Vasudev", first_embedding), (True, True, False))
        self.assertEqual(self.repository.save_embedding("Vasudev", second_embedding), (True, True, True))

        users = self.repository.list_users()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0]["template_count"], 2)

    def test_delete_user_uses_repository_identifier_validation(self) -> None:
        self.repository.create_user("Vasudev", [[0.1, 0.2]])
        user_id = self.repository.list_users()[0]["id"]

        self.assertTrue(self.repository.delete_user(user_id))
        self.assertFalse(self.repository.delete_user(user_id))
        with self.assertRaises(ValueError):
            self.repository.delete_user("not-an-object-id")


class AttendanceRepositoryTest(unittest.TestCase):
    def setUp(self) -> None:
        self.repository = AttendanceRepository(_MemoryDatabase())
        self.record = {
            "user_id": "registered-user",
            "name": "Vasudev",
            "date": "2026-05-23",
            "timestamp": "2026-05-23T09:00:00",
            "confidence": 98.4,
            "was_corrected": False,
            "original_prediction": "Vasudev",
        }

    def test_registered_user_attendance_is_stored_once_per_date(self) -> None:
        self.assertTrue(self.repository.insert_once(self.record))
        self.assertFalse(self.repository.insert_once(self.record))
        self.assertTrue(self.repository.is_marked("registered-user", "2026-05-23"))
        self.assertEqual(self.repository.total_count(), 1)
        self.assertEqual(len(self.repository.by_date("2026-05-23")), 1)

    def test_correction_log_is_inserted_through_repository(self) -> None:
        correction = {
            "timestamp": "2026-05-23T09:00:00",
            "face_box": {"left": 1, "top": 2, "right": 3, "bottom": 4},
            "original_prediction": "Other Name",
            "original_confidence": 70.0,
            "corrected_to": "Vasudev",
            "corrected_user_id": "registered-user",
            "image_context": "upload",
        }

        self.assertTrue(self.repository.insert_correction(correction))
        self.assertEqual(self.repository.corrections()[0]["corrected_to"], "Vasudev")


if __name__ == "__main__":
    unittest.main()
