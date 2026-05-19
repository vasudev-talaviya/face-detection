import cv2
import numpy as np
from insightface.app import FaceAnalysis

# =========================
# LOAD MODEL ONLY ONE TIME
# =========================

# Initialize InsightFace FaceAnalysis (buffalo_l is highly accurate)
face_analysis = FaceAnalysis(name='buffalo_l')
face_analysis.prepare(ctx_id=-1, det_size=(640, 640))

# Minimum face size to accept — filters out tiny group photo faces
MIN_FACE_SIZE = 80  # pixels

# =========================
# FACE DETECTION FUNCTION
# =========================

def detect_face(frame, compute_embeddings=True, num_jitters=1, upsample=1):
    """
    Args:
        frame:             BGR image (from cv2)
        compute_embeddings: Whether to compute 512-d face vectors using InsightFace
        num_jitters:       Not used (kept for backward compatibility)
        upsample:          Not used (kept for backward compatibility)
    """

    # Detect faces using InsightFace (takes BGR frame directly)
    faces = face_analysis.get(frame)

    print(f"Total faces detected: {len(faces)}")

    face_embeddings = []
    face_boxes = []
    skipped = 0

    for i, face in enumerate(faces, start=1):
        bbox = face.bbox.astype(int)
        left   = bbox[0]
        top    = bbox[1]
        right  = bbox[2]
        bottom = bbox[3]

        # Clamp coordinates to frame boundary to prevent out of bounds
        h, w = frame.shape[:2]
        left   = max(0, min(left, w - 1))
        top    = max(0, min(top, h - 1))
        right  = max(0, min(right, w - 1))
        bottom = max(0, min(bottom, h - 1))

        face_w = right - left
        face_h = bottom - top

        # Skip small faces (group photo noise)
        if face_w < MIN_FACE_SIZE or face_h < MIN_FACE_SIZE:
            print(f"  ⚠️  Face {i} skipped — too small ({face_w}x{face_h}px < {MIN_FACE_SIZE}px min)")
            skipped += 1
            # Still draw box but in red to show it was rejected
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 200), 1)
            cv2.putText(frame, "Too Small", (left, top - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 200), 1)
            continue

        face_boxes.append((left, top, right, bottom))

        print(f"  Face {i}: left={left}, top={top}, right={right}, bottom={bottom} | size={face_w}x{face_h}px")

        if compute_embeddings:
            # Convert 512-d float numpy array to list for JSON/DB serialization
            embedding = face.embedding.tolist()
            face_embeddings.append(embedding)

        # Draw bounding box (green for accepted)
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

    h, w = frame.shape[:2]
    accepted = len(faces) - skipped

    # HUD: face count
    cv2.putText(
        frame,
        f"Faces: {accepted} accepted, {skipped} skipped (too small)",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        min(w, h) / 900,
        (0, 254, 255),
        2
    )

    return frame, face_embeddings, face_boxes

