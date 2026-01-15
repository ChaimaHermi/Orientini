from datetime import datetime
from typing import Optional, Dict, List
from pydantic import BaseModel, Field

class Message(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    conversation_id: str
    role: str  # "user" | "assistant"

    # ✅ TEXTE
    content: str

    # ✅ IMAGES MURAG (OPTIONNEL)
    images: Optional[Dict[str, List[str]]] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        validate_by_name = True
