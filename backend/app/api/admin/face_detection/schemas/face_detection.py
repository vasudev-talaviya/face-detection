from pydantic import BaseModel, Field


class FaceDetectionRequest(BaseModel):
    image: str = Field(min_length=1, description="A base64 encoded image or image data URL.")
