from pydantic import BaseModel, Field

from app.db.models.fields import FaceEmbedding, PersonName


class UserDocument(BaseModel):
    name: PersonName
    embedding: list[FaceEmbedding] = Field(min_length=1)
