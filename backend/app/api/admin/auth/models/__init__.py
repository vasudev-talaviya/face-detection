from pydantic import BaseModel, EmailStr


class UserAuthDocument(BaseModel):
    email: EmailStr
    hashed_password: str
    is_active: bool = True
    role: str = "admin"
