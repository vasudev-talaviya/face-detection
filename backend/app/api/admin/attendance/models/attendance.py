from datetime import date as CalendarDate
from datetime import datetime

from pydantic import BaseModel

from app.db.models.fields import Confidence, FaceBox, ImageContext, PersonName


class AttendanceDocument(BaseModel):
    user_id: str | None = None
    name: PersonName
    date: CalendarDate
    timestamp: datetime
    confidence: Confidence
    was_corrected: bool
    original_prediction: PersonName | None = None


class CorrectionLogDocument(BaseModel):
    timestamp: datetime
    face_box: FaceBox | None = None
    original_prediction: PersonName | None = None
    original_confidence: Confidence
    corrected_to: PersonName
    corrected_user_id: str | None = None
    image_context: ImageContext
