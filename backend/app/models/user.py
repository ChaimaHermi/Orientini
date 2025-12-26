from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class User(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")

    email: EmailStr
    hashed_password: Optional[str] = None

    role: str = "student"          # student | admin
    remember_me: bool = False

    profile_picture: Optional[str] = None
    google_id: Optional[str] = None

    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
