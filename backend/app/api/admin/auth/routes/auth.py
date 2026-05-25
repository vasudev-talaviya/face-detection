from fastapi import APIRouter, Depends
from app.api.admin.auth.schemas import (
    RegisterAuthRequest,
    LoginAuthRequest,
    RefreshAuthRequest,
    ForgotPasswordRequest,
    VerifyOTPRequest,
)
from app.api.admin.auth.dependencies import get_auth_service, get_current_user
from app.api.admin.auth.services import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", summary="Register admin credentials")
def register(request: RegisterAuthRequest, service: AuthService = Depends(get_auth_service)):
    return service.register(request.email, request.password)


@router.post("/login", summary="Login admin user")
def login(request: LoginAuthRequest, service: AuthService = Depends(get_auth_service)):
    return service.login(request.email, request.password)


@router.post("/refresh", summary="Refresh access token")
def refresh(request: RefreshAuthRequest, service: AuthService = Depends(get_auth_service)):
    return service.refresh_token(request.refresh_token)


@router.post("/forgot-password", summary="Initiate password recovery")
def forgot_password(request: ForgotPasswordRequest, service: AuthService = Depends(get_auth_service)):
    return service.forgot_password(request.email)


@router.post("/verify-otp", summary="Verify one-time password")
def verify_otp(request: VerifyOTPRequest, service: AuthService = Depends(get_auth_service)):
    return service.verify_otp(request.email, request.otp)


@router.get("/me", summary="Get details of currently authenticated admin")
def get_me(current_user: dict = Depends(get_current_user)):
    return {"email": current_user.get("sub"), "role": current_user.get("role")}
