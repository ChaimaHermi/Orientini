import os
import secrets
from datetime import datetime

from app.core.config import settings
from app.models.user import User
from app.utils.password import hash_password, verify_password
from app.utils.jwt import create_access_token
from app.utils.email import send_reset_email
from app.utils.google_oauth import get_google_user_info


def create_admin_if_not_exists(db):
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")

    if not admin_email or not admin_password:
        return

    if db.users.find_one({"email": admin_email, "role": "admin"}):
        return

    admin_user = User(
        email=admin_email,
        hashed_password=hash_password(admin_password),
        role="admin",
        remember_me=True
    )

    db.users.insert_one(
        admin_user.model_dump(exclude={"id"}, exclude_none=True)
    )

    print("✅ Admin user created")


def register(email: str, password: str, remember_me: bool, db):
    if db.users.find_one({"email": email}):
        raise ValueError("User already exists")

    user = User(
        email=email,
        hashed_password=hash_password(password),
        remember_me=remember_me
    )

    db.users.insert_one(
        user.model_dump(exclude={"id"}, exclude_none=True)
    )

    return create_access_token(
        {"sub": email, "role": user.role},
        remember_me=remember_me
    )


def login(email: str, password: str, remember_me: bool, db):
    user = db.users.find_one({"email": email})

    if not user or not verify_password(password, user["hashed_password"]):
        raise ValueError("Invalid credentials")

    return create_access_token(
        {"sub": email, "role": user["role"]},
        remember_me=remember_me
    )


def forgot_password(email: str, db):
    user = db.users.find_one({"email": email})
    if not user:
        return

    reset_token = secrets.token_urlsafe(32)

    db.users.update_one(
        {"email": email},
        {"$set": {
            "reset_token": reset_token,
            "reset_token_created_at": datetime.utcnow()
        }}
    )

    reset_link = (
        f"{settings.FRONTEND_URL}/auth/reset-password"
        f"?token={reset_token}"
    )

    send_reset_email(email, reset_link)


def reset_password(token: str, new_password: str, db):
    user = db.users.find_one({"reset_token": token})
    if not user:
        raise ValueError("Invalid token")

    db.users.update_one(
        {"_id": user["_id"]},
        {
            "$set": {"hashed_password": hash_password(new_password)},
            "$unset": {"reset_token": "", "reset_token_created_at": ""}
        }
    )


def login_with_google(code: str, db):
    user_info = get_google_user_info(code)

    email = user_info["email"]
    picture = user_info.get("picture")

    user = db.users.find_one({"email": email})

    if not user:
        new_user = User(
            email=email,
            google_id=user_info["id"],
            profile_picture=picture,
            remember_me=True
        )
        db.users.insert_one(
            new_user.model_dump(exclude={"id"}, exclude_none=True)
        )
        role = "student"
    else:
        db.users.update_one(
            {"_id": user["_id"]},
            {"$set": {"profile_picture": picture}}
        )
        role = user.get("role", "student")

    return create_access_token(
        {"sub": email, "role": role},
        remember_me=True
    )
