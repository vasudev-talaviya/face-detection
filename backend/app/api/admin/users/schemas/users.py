from pydantic import BaseModel

from app.db.models.fields import FaceEmbedding, PersonName


class RegisterUserRequest(BaseModel):
    """A face template supplied when registering or extending a user profile."""

    name: PersonName
    image: str


class UpdateUserRequest(BaseModel):
    """Payload for updating a user's details."""
    
    name: PersonName
    image: str | None = None
