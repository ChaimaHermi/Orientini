from pydantic import BaseModel
from datetime import datetime


class ConversationResponse(BaseModel):
    id: str
    title: str
    created_at: datetime