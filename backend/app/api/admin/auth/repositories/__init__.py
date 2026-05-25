from bson import ObjectId
from app.core.base import BaseRepository
from app.db.mongo import get_database


class AuthRepository(BaseRepository):
    def __init__(self, database=None) -> None:
        database = database if database is not None else get_database()
        self.collection = database["AdminCredentials"]
        self.otp_collection = database["OTPStore"]

    def get_by_id(self, id: str) -> dict | None:
        return self.collection.find_one({"_id": ObjectId(id)})

    def get_all(self) -> list[dict]:
        return list(self.collection.find())

    def create(self, data: dict) -> str | None:
        res = self.collection.insert_one(data)
        return str(res.inserted_id) if res.inserted_id else None

    def update(self, id: str, data: dict) -> bool:
        res = self.collection.update_one({"_id": ObjectId(id)}, {"$set": data})
        return res.modified_count > 0

    def delete(self, id: str) -> bool:
        res = self.collection.delete_one({"_id": ObjectId(id)})
        return res.deleted_count > 0

    def get_by_email(self, email: str) -> dict | None:
        return self.collection.find_one({"email": email})

    def store_otp(self, email: str, otp: str) -> None:
        self.otp_collection.update_one(
            {"email": email},
            {"$set": {"otp": otp}},
            upsert=True,
        )

    def verify_otp(self, email: str, otp: str) -> bool:
        record = self.otp_collection.find_one({"email": email})
        if record and record.get("otp") == otp:
            self.otp_collection.delete_one({"email": email})
            return True
        return False
