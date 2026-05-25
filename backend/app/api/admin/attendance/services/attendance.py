from datetime import date

from app.api.admin.attendance.schemas.attendance import AttendanceSubmissionRequest
from app.core.base import APIResponse, BaseService
from app.core.logging import get_logger
from app.api.admin.attendance.repositories.attendance import AttendanceRepository
from app.api.common.utils.dates import now_string, today_string

logger = get_logger(__name__)


class AttendanceService(BaseService):
    def __init__(self, repository: AttendanceRepository) -> None:
        super().__init__(repository)
        self.repository = repository
        logger.info("AttendanceService initialized")

    def submit(self, request: AttendanceSubmissionRequest) -> dict:
        attendance_date = today_string()
        timestamp = now_string()
        results = []
        inserted_count = skipped_count = corrected_count = 0

        for entry in request.entries:
            record = {
                "user_id": entry.user_id,
                "name": entry.final_name,
                "date": attendance_date,
                "timestamp": timestamp,
                "confidence": entry.confidence,
                "was_corrected": entry.was_corrected,
                "original_prediction": entry.original_prediction or entry.final_name,
            }
            if not self.repository.insert_once(record):
                results.append(
                    {
                        "name": entry.final_name,
                        "status": "already_marked",
                        "message": f"{entry.final_name} already marked present today",
                    }
                )
                skipped_count += 1
                logger.info(f"{entry.final_name} already marked for {attendance_date}")
                continue

            inserted_count += 1
            if entry.was_corrected:
                self.repository.insert_correction(
                    {
                        "timestamp": timestamp,
                        "face_box": entry.face_box.model_dump() if entry.face_box else None,
                        "original_prediction": entry.original_prediction,
                        "original_confidence": entry.confidence,
                        "corrected_to": entry.final_name,
                        "corrected_user_id": entry.user_id,
                        "image_context": request.image_context,
                    }
                )
                corrected_count += 1
                logger.info(f"Attendance corrected for {entry.final_name}")
            
            results.append(
                {
                    "name": entry.final_name,
                    "status": "marked",
                    "message": f"{entry.final_name} marked present",
                }
            )

        logger.info(
            f"Attendance submission: {inserted_count} inserted, "
            f"{skipped_count} skipped, {corrected_count} corrected"
        )
        
        return APIResponse.success(
            data={
                "inserted": inserted_count,
                "skipped": skipped_count,
                "corrected": corrected_count,
                "results": results,
            },
            message="Attendance submitted successfully"
        )

    def attendance_for_date(self, attendance_date: date) -> dict:
        date_string = attendance_date.isoformat()
        records = self.repository.by_date(date_string)
        logger.info(f"Retrieved {len(records)} attendance records for {date_string}")
        return APIResponse.success(
            data={
                "date": date_string,
                "count": len(records),
                "records": records,
            },
            message="Attendance records retrieved successfully"
        )

    def attendance_for_user(self, user_id: str) -> dict:
        records = self.repository.by_user(user_id)
        logger.info(f"Retrieved {len(records)} attendance records for user {user_id}")
        return APIResponse.success(
            data={
                "user_id": user_id,
                "count": len(records),
                "records": records,
            },
            message="User attendance history retrieved successfully"
        )

    def corrections(self) -> dict:
        corrections = self.repository.corrections()
        total_attendance = self.repository.total_count()
        confusion_map: dict[str, dict] = {}
        
        for correction in corrections:
            original = correction.get("original_prediction") or "Unknown"
            summary = confusion_map.setdefault(original, {"count": 0, "corrected_to": []})
            summary["count"] += 1
            corrected_to = correction.get("corrected_to", "")
            if corrected_to not in summary["corrected_to"]:
                summary["corrected_to"].append(corrected_to)
        
        most_confused = sorted(confusion_map.items(), key=lambda item: item[1]["count"], reverse=True)
        rate = len(corrections) / total_attendance * 100 if total_attendance else 0
        
        logger.info(
            f"Correction statistics: {len(corrections)} corrections, "
            f"{total_attendance} total attendance, {rate:.1f}% correction rate"
        )
        
        return APIResponse.success(
            data={
                "total_corrections": len(corrections),
                "total_attendance": total_attendance,
                "correction_rate": round(rate, 1),
                "corrections": corrections[:50],
                "most_confused": [
                    {"name": name, "count": data["count"], "corrected_to": data["corrected_to"]}
                    for name, data in most_confused[:10]
                ],
            },
            message="Correction statistics retrieved successfully"
        )
