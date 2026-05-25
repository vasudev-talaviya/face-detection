from pydantic import BaseModel, EmailStr


class RegisterAuthRequest(BaseModel):
    email: EmailStr
    password: str


class LoginAuthRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshAuthRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp: str
