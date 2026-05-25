from pydantic import BaseModel, Field

from app.db.models.fields import Confidence, FaceBox, ImageContext, PersonName


class AttendanceEntryRequest(BaseModel):
    user_id: str | None = None
    final_name: PersonName
    original_prediction: PersonName | None = None
    confidence: Confidence = 0.0
    was_corrected: bool = False
    face_box: FaceBox | None = None


class AttendanceSubmissionRequest(BaseModel):
    entries: list[AttendanceEntryRequest] = Field(min_length=1, max_length=100)
    image_context: ImageContext = "upload"


class AttendanceUpdateRequest(BaseModel):
    status: str | None = None
    was_corrected: bool | None = None
    confidence: float | None = None
