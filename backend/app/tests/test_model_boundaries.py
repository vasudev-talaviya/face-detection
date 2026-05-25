import math
import unittest

from pydantic import ValidationError

from app.api.admin.attendance.schemas.attendance import AttendanceEntryRequest
from app.api.admin.users.schemas.users import RegisterUserRequest
from app.api.admin.attendance.models.attendance import AttendanceDocument, CorrectionLogDocument
from app.api.admin.users.models.users import UserDocument


class DatabaseModelValidationTest(unittest.TestCase):
    def test_person_names_are_normalized_at_request_and_document_boundaries(self) -> None:
        request = AttendanceEntryRequest(final_name="  Vasudev   Kumar  ")
        document = AttendanceDocument(
            user_id="user-id",
            name="  Vasudev   Kumar  ",
            date="2026-05-23",
            timestamp="2026-05-23T09:00:00",
            confidence=98.4,
            was_corrected=False,
            original_prediction="  Vasudev   Kumar  ",
        )

        self.assertEqual(request.final_name, "Vasudev Kumar")
        self.assertEqual(document.name, request.final_name)
        self.assertEqual(document.original_prediction, request.final_name)

    def test_embeddings_are_validated_for_requests_and_documents(self) -> None:
        with self.assertRaises(ValidationError):
            RegisterUserRequest(name="Vasudev", embedding=[math.inf])
        with self.assertRaises(ValidationError):
            UserDocument(name="Vasudev", embedding=[[math.nan]])

    def test_face_box_validation_is_shared_with_correction_documents(self) -> None:
        with self.assertRaises(ValidationError):
            AttendanceEntryRequest(
                final_name="Vasudev",
                face_box={"left": 10, "top": 5, "right": 10, "bottom": 20},
            )
        with self.assertRaises(ValidationError):
            CorrectionLogDocument(
                timestamp="2026-05-23T09:00:00",
                face_box={"left": 10, "top": 5, "right": 10, "bottom": 20},
                original_prediction="Other",
                original_confidence=70.0,
                corrected_to="Vasudev",
                corrected_user_id="user-id",
                image_context="upload",
            )

    def test_document_dates_are_validated_as_iso_values(self) -> None:
        with self.assertRaises(ValidationError):
            AttendanceDocument(
                name="Vasudev",
                date="not-a-date",
                timestamp="not-a-timestamp",
                confidence=98.4,
                was_corrected=False,
                original_prediction="Vasudev",
            )


if __name__ == "__main__":
    unittest.main()
