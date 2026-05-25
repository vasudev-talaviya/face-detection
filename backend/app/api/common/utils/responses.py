"""Shared utilities for responses and detection results."""

from dataclasses import dataclass

from app.core.base import APIResponse


@dataclass
class DetectionBox:
    """Standardized detection box representation."""

    left: int
    top: int
    right: int
    bottom: int

    @staticmethod
    def from_tuple(box: tuple[int, int, int, int]) -> "DetectionBox":
        """Create from tuple (left, top, right, bottom)."""
        left, top, right, bottom = box
        return DetectionBox(
            left=int(left),
            top=int(top),
            right=int(right),
            bottom=int(bottom),
        )

    def to_dict(self) -> dict[str, int]:
        """Convert to dictionary."""
        return {
            "left": self.left,
            "top": self.top,
            "right": self.right,
            "bottom": self.bottom,
        }


class DetectionResponseBuilder:
    """Builder for consistent detection response format."""

    @staticmethod
    def face_match_result(
        box: tuple[int, int, int, int],
        is_new_face: bool,
        confidence: float,
        matched_name: str | None = None,
        embedding: list[float] | None = None,
        **extras,
    ) -> dict:
        """Build standardized face match result."""
        result = {
            "box": DetectionBox.from_tuple(box).to_dict(),
            "is_new_face": is_new_face,
            "name": matched_name,
            "confidence": float(confidence),
        }
        result.update(extras)
        return result

    @staticmethod
    def detection_response(
        annotated_image: str,
        faces: list[dict],
        **extras,
    ) -> dict:
        """Build standardized detection API response."""
        return APIResponse.success(
            data={
                "annotated_image": annotated_image,
                "face_count": len(faces),
                "faces": faces,
                **extras,
            },
            message="Detection completed successfully",
        )
