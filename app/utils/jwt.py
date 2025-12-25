from datetime import datetime, timedelta
from jose import jwt
from app.core.config import settings

def create_access_token(data: dict, remember_me: bool = False) -> str:
    expire = (
        datetime.utcnow() + timedelta(days=settings.JWT_EXPIRATION_REMEMBER_DAYS)
        if remember_me
        else datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
    )

    payload = data.copy()
    payload["exp"] = expire

    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
