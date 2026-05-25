import base64
import binascii

import cv2
import numpy as np

from app.core.exceptions import BadRequestError


def decode_image(image: str, max_bytes: int) -> np.ndarray:
    payload = image
    if image.startswith("data:"):
        try:
            metadata, payload = image.split(",", 1)
        except ValueError as exc:
            raise BadRequestError("Invalid image data URL.") from exc
        if not metadata.startswith("data:image/") or ";base64" not in metadata:
            raise BadRequestError("Only base64 image data URLs are supported.")

    try:
        image_bytes = base64.b64decode(payload, validate=True)
    except (ValueError, binascii.Error) as exc:
        raise BadRequestError("Invalid base64 image data.") from exc

    if not image_bytes:
        raise BadRequestError("Image cannot be empty.")
    if len(image_bytes) > max_bytes:
        raise BadRequestError("Decoded image is too large.")

    frame = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)
    if frame is None:
        raise BadRequestError("Invalid image data.")
    return frame


def encode_jpeg_data_url(frame: np.ndarray, quality: int = 90) -> str:
    success, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
    if not success:
        raise RuntimeError("Could not encode processed image.")
    encoded = base64.b64encode(buffer).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"


def crop_with_padding(frame: np.ndarray, box: tuple[int, int, int, int], padding: int = 15) -> np.ndarray:
    left, top, right, bottom = box
    height, width = frame.shape[:2]
    return frame[
        max(0, top - padding):min(height, bottom + padding),
        max(0, left - padding):min(width, right + padding),
    ]
