from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Message(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    conversation_id: str
    role: str  # "user" | "assistant"
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
