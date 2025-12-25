from jose import jwt, JWTError
from fastapi import HTTPException, status
from pymongo import MongoClient

from app.core.config import settings

client = MongoClient(settings.MONGO_URI)
db = client[settings.MONGO_DB]
users = db.users


def get_current_user(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        email: str | None = payload.get("sub")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        user = users.find_one({"email": email})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Nettoyage Mongo
        user["id"] = str(user["_id"])
        user.pop("_id")
        user.pop("hashed_password", None)

        return user

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
