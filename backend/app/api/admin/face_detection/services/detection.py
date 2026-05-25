from app.core.base import BaseService
from app.core.logging import get_logger
from app.api.admin.attendance.repositories.attendance import AttendanceRepository
from app.api.admin.users.repositories.users import FaceMatch, UserRepository
from app.api.common.utils.dates import today_string
from app.api.common.utils.images import crop_with_padding, decode_image, encode_jpeg_data_url
from app.api.common.utils.responses import DetectionResponseBuilder

logger = get_logger(__name__)


class DetectionService(BaseService):
    def __init__(
        self,
        user_repository: UserRepository,
        attendance_repository: AttendanceRepository,
        max_image_bytes: int,
    ) -> None:
        super().__init__(user_repository)
        self.users = user_repository
        self.attendance = attendance_repository
        self.max_image_bytes = max_image_bytes
        logger.info("DetectionService initialized")

    def _analyse(self, image: str):
        source_frame = decode_image(image, self.max_image_bytes)
        annotated_frame = source_frame.copy()

        # Model loading is deferred until an endpoint genuinely needs detection.
        from app.ml.detector import detect_face

        annotated_frame, embeddings, boxes = detect_face(annotated_frame, compute_embeddings=True)
        return source_frame, annotated_frame, embeddings, boxes

    def detect_faces(self, image: str) -> dict:
        _, annotated, embeddings, boxes = self._analyse(image)
        records = self.users.face_records()
        faces = []
        for embedding, box in zip(embeddings, boxes):
            match = self.users.match_embedding(embedding, records)
            faces.append(
                DetectionResponseBuilder.face_match_result(
                    box=box,
                    is_new_face=match.is_new_face,
                    confidence=match.confidence,
                    matched_name=match.matched_name,
                )
            )
        return DetectionResponseBuilder.detection_response(
            annotated_image=encode_jpeg_data_url(annotated),
            faces=faces,
        )

    def detect_attendance_faces(self, image: str) -> dict:
        source, annotated, embeddings, boxes = self._analyse(image)
        marked_date = today_string()
        records = self.users.face_records()
        faces = []
        for index, (embedding, box) in enumerate(zip(embeddings, boxes), start=1):
            match = self.users.match_embedding(embedding, records)
            faces.append(
                DetectionResponseBuilder.face_match_result(
                    box=box,
                    is_new_face=match.is_new_face,
                    confidence=match.confidence,
                    matched_name=match.matched_name,
                    index=index,
                    user_id=match.user_id,
                    thumbnail=encode_jpeg_data_url(crop_with_padding(source, box), quality=85),
                    already_marked=self.attendance.is_marked(match.user_id, marked_date),
                )
            )
        return DetectionResponseBuilder.detection_response(
            annotated_image=encode_jpeg_data_url(annotated),
            faces=faces,
        )
