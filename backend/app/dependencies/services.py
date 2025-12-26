from fastapi import Depends
from app.dependencies.database import database
from app.services.conversation_service import ConversationService


def conversation_service(
    db=Depends(database)
):
    return ConversationService(db)
