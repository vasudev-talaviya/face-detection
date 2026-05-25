from bson import ObjectId
from pymongo import ASCENDING
from pymongo.errors import DuplicateKeyError

from app.core.base import BaseRepository
from app.core.logging import get_logger
from app.api.admin.attendance.models.attendance import AttendanceDocument, CorrectionLogDocument
from app.db.mongo import get_database

logger = get_logger(__name__)


class AttendanceRepository(BaseRepository):
    """Database operations for attendance and correction records."""

    def _map_id(self, record: dict) -> dict:
        if not record:
            return record
        if "_id" in record:
            record["id"] = str(record.pop("_id"))
        return record

    def __init__(self, database=None) -> None:
        database = database if database is not None else get_database()
        self.attendance = database["Attendance"]
        self.correction_logs = database["CorrectionLog"]
        self._indexes_ready = False
        logger.info("AttendanceRepository initialized")

    # Abstract method implementations
    def get_by_id(self, id: str) -> dict | None:
        """Retrieve attendance record by ID."""
        try:
            return self.attendance.find_one({"_id": ObjectId(id)})
        except Exception as e:
            logger.warning(f"Error retrieving attendance record: {e}")
            return None

    def get_all(self) -> list[dict]:
        """Retrieve all attendance records."""
        return [self._map_id(r) for r in self.attendance.find({})]

    def create(self, data: dict) -> bool:
        """Create new attendance record."""
        try:
            result = self.attendance.insert_one(data)
            return bool(result.inserted_id)
        except Exception as e:
            logger.error(f"Error creating attendance record: {e}")
            return False

    def update(self, id: str, data: dict) -> bool:
        """Update attendance record by ID."""
        try:
            result = self.attendance.update_one({"_id": ObjectId(id)}, {"$set": data})
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating attendance record: {e}")
            return False

    def delete(self, id: str) -> bool:
        """Delete attendance record by ID."""
        try:
            result = self.attendance.delete_one({"_id": ObjectId(id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting attendance record: {e}")
            return False

    # Core repository methods

    def ensure_indexes(self) -> None:
        if self._indexes_ready:
            return
        self.attendance.create_index(
            [("user_id", ASCENDING), ("date", ASCENDING)],
            name="unique_registered_user_attendance_date",
            unique=True,
            partialFilterExpression={"user_id": {"$type": "string"}},
        )
        self._indexes_ready = True

    def is_marked(self, user_id: str | None, date_string: str) -> bool:
        if not user_id:
            return False
        return self.attendance.find_one({"user_id": user_id, "date": date_string}) is not None

    def insert_once(self, record_data: dict) -> bool:
        """Atomically create one daily attendance record for registered users."""
        record = AttendanceDocument(**record_data).model_dump(mode="json")
        if not record["user_id"]:
            return bool(self.attendance.insert_one(record).inserted_id)
        self.ensure_indexes()
        try:
            result = self.attendance.update_one(
                {"user_id": record["user_id"], "date": record["date"]},
                {"$setOnInsert": record},
                upsert=True,
            )
        except DuplicateKeyError:
            return False
        return result.upserted_id is not None

    def insert_correction(self, correction_data: dict) -> bool:
        record = CorrectionLogDocument(**correction_data).model_dump(mode="json")
        return bool(self.correction_logs.insert_one(record).inserted_id)

    def by_date(self, date_string: str) -> list[dict]:
        return [self._map_id(r) for r in self.attendance.find({"date": date_string}).sort("timestamp", -1)]

    def by_user(self, user_id: str) -> list[dict]:
        return [self._map_id(r) for r in self.attendance.find({"user_id": user_id}).sort("timestamp", -1)]

    def corrections(self) -> list[dict]:
        return list(self.correction_logs.find({}, {"_id": 0}).sort("timestamp", -1))

    def total_count(self) -> int:
        return self.attendance.count_documents({})
