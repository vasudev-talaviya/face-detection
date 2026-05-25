from datetime import timedelta
from app.core.base import BaseService, APIResponse
from app.core.config import get_settings
from app.core.exceptions import BadRequestError, NotFoundError, UnauthorizedError
from app.api.admin.auth.repositories import AuthRepository
from app.api.admin.auth.utils import hash_password, verify_password, create_token, generate_otp
from app.api.admin.auth.constants import ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS


class AuthService(BaseService):
    def __init__(self, repository: AuthRepository) -> None:
        super().__init__(repository)
        self.repository = repository

    def register(self, email: str, password: str) -> dict:
        existing = self.repository.get_by_email(email)
        if existing:
            raise BadRequestError("Email is already registered.")
        
        hashed = hash_password(password)
        user_id = self.repository.create({
            "email": email,
            "hashed_password": hashed,
            "is_active": True,
            "role": "admin"
        })
        
        return APIResponse.success(
            data={"user_id": user_id},
            message="Admin registered successfully"
        )

    def login(self, email: str, password: str) -> dict:
        user = self.repository.get_by_email(email)
        if not user or not verify_password(password, user["hashed_password"]):
            raise UnauthorizedError("Incorrect email or password")
            
        settings = get_settings()
        secret_key = settings.api_key or "default_secret_key"
        
        access_token = create_token(
            {"sub": email, "role": user.get("role", "admin")},
            timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
            secret_key
        )
        refresh_token = create_token(
            {"sub": email, "type": "refresh"},
            timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
            secret_key
        )
        
        return APIResponse.success(
            data={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer"
            },
            message="Logged in successfully"
        )

    def refresh_token(self, refresh_token: str) -> dict:
        # Simplistic mock token validation/refresh
        settings = get_settings()
        secret_key = settings.api_key or "default_secret_key"
        
        from app.api.admin.auth.utils import decode_token
        payload = decode_token(refresh_token, secret_key)
        if not payload or payload.get("type") != "refresh":
            raise UnauthorizedError("Invalid refresh token")
            
        email = payload.get("sub")
        access_token = create_token(
            {"sub": email, "role": "admin"},
            timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
            secret_key
        )
        
        return APIResponse.success(
            data={
                "access_token": access_token,
                "token_type": "bearer"
            },
            message="Token refreshed successfully"
        )

    def forgot_password(self, email: str) -> dict:
        user = self.repository.get_by_email(email)
        if not user:
            raise NotFoundError("User not found")
            
        otp = generate_otp()
        self.repository.store_otp(email, otp)
        
        # In a real environment, we would email this OTP.
        return APIResponse.success(
            data={"otp_preview": otp},  # Previewing it for stub convenience
            message="OTP sent to registered email address"
        )

    def verify_otp(self, email: str, otp: str) -> dict:
        if not self.repository.verify_otp(email, otp):
            raise BadRequestError("Invalid or expired OTP")
            
        return APIResponse.success(
            message="OTP verified successfully. You may now reset your password."
        )
