import logging

import cv2
from insightface.app import FaceAnalysis

logger = logging.getLogger(__name__)

# The expensive detector is initialized once, when the detection service first uses it.
face_analysis = FaceAnalysis(name="buffalo_l")
face_analysis.prepare(ctx_id=-1, det_size=(640, 640))

MIN_FACE_SIZE = 80


def detect_face(frame, compute_embeddings=True, num_jitters=1, upsample=1):
    """Detect accepted faces, draw boxes, and optionally return embeddings."""
    faces = face_analysis.get(frame)
    logger.debug("Detected %d raw faces", len(faces))

    face_embeddings = []
    face_boxes = []
    skipped = 0

    for index, face in enumerate(faces, start=1):
        left, top, right, bottom = face.bbox.astype(int)
        height, width = frame.shape[:2]
        left = max(0, min(left, width - 1))
        top = max(0, min(top, height - 1))
        right = max(0, min(right, width - 1))
        bottom = max(0, min(bottom, height - 1))
        face_width = right - left
        face_height = bottom - top

        if face_width < MIN_FACE_SIZE or face_height < MIN_FACE_SIZE:
            logger.debug("Skipping face %d because it is too small: %dx%d", index, face_width, face_height)
            skipped += 1
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 200), 1)
            cv2.putText(
                frame,
                "Too Small",
                (left, top - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (0, 0, 200),
                1,
            )
            continue

        face_boxes.append((left, top, right, bottom))
        if compute_embeddings:
            face_embeddings.append(face.embedding.tolist())
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

    height, width = frame.shape[:2]
    accepted = len(faces) - skipped
    cv2.putText(
        frame,
        f"Faces: {accepted} accepted, {skipped} skipped (too small)",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        min(width, height) / 900,
        (0, 254, 255),
        2,
    )
    return frame, face_embeddings, face_boxes
