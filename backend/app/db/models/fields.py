import math
from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel, Field, model_validator

MAX_PERSON_NAME_LENGTH = 120


def normalize_person_name(value: str) -> str:
    normalized = " ".join(value.split())
    if not normalized:
        raise ValueError("Name cannot be empty.")
    if len(normalized) > MAX_PERSON_NAME_LENGTH:
        raise ValueError(f"Name cannot exceed {MAX_PERSON_NAME_LENGTH} characters.")
    return normalized


def validate_face_embedding(value: list[float]) -> list[float]:
    if not all(math.isfinite(component) for component in value):
        raise ValueError("Embedding values must be finite numbers.")
    return value


PersonName = Annotated[str, AfterValidator(normalize_person_name)]
Confidence = Annotated[float, Field(ge=0.0, le=100.0)]
ImageContext = Literal["upload", "webcam"]
FaceEmbedding = Annotated[
    list[float],
    Field(min_length=1, max_length=4096),
    AfterValidator(validate_face_embedding),
]


class FaceBox(BaseModel):
    left: int
    top: int
    right: int
    bottom: int

    @model_validator(mode="after")
    def validate_dimensions(self) -> "FaceBox":
        if self.right <= self.left or self.bottom <= self.top:
            raise ValueError("Face box must have positive width and height.")
        return self
