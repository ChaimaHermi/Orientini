from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    role: str
    profile_picture: Optional[str] = None
    is_active: bool
    created_at: datetime
