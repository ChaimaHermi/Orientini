from pydantic import BaseModel, EmailStr


# REQUESTS

class RegisterSchema(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False


class LoginSchema(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False


class ForgotPasswordSchema(BaseModel):
    email: EmailStr


class ResetPasswordSchema(BaseModel):
    token: str
    new_password: str


# RESPONSES

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
