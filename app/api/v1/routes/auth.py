from fastapi import APIRouter, HTTPException, Query
from app.schemas.auth import (
    RegisterSchema,
    LoginSchema,
    ForgotPasswordSchema,
    ResetPasswordSchema,
    TokenResponse
)
from app.services import auth_service
from fastapi.responses import RedirectResponse
from app.core.config import settings


router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post("/register", response_model=TokenResponse)
def register(data: RegisterSchema):
    try:
        token = auth_service.register(
            email=data.email,
            password=data.password,
            remember_me=data.remember_me
        )
        return {"access_token": token}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenResponse)
def login(data: LoginSchema):
    try:
        token = auth_service.login(
            email=data.email,
            password=data.password,
            remember_me=data.remember_me
        )
        return {"access_token": token}
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid credentials")


@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordSchema):
    auth_service.forgot_password(data.email)
    return {"message": "If the email exists, a reset link has been sent."}


@router.post("/reset-password")
def reset_password(data: ResetPasswordSchema):
    try:
        auth_service.reset_password(
            token=data.token,
            new_password=data.new_password
        )
        return {"message": "Password reset successful"}
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")


@router.get("/google/callback")
def google_callback(
    code: str | None = Query(default=None),
    error: str | None = Query(default=None)
):
    if error:
        # L'utilisateur a refusé ou annulé
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/auth/login"
        )

    token = auth_service.login_with_google(code)

    return RedirectResponse(
        url=f"{settings.FRONTEND_URL}/auth/callback?token={token}&rememberMe=true"
    )
