from fastapi import APIRouter, Depends, HTTPException, Form
from app.dependencies.services import conversation_service
from app.services.user_service import get_current_user

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)

@router.post("/ask")
def ask_question(
    question: str = Form(...),
    conversation_id: str | None = Form(None),
    service=Depends(conversation_service),
    user=Depends(get_current_user)
):
    return service.ask(
        user_id=user["id"],
        question=question,
        conversation_id=conversation_id
    )

@router.get("/conversations")
def get_user_conversations(
    service=Depends(conversation_service),
    user=Depends(get_current_user)
):
    return service.get_user_conversations(user["id"])

@router.get("/conversations/{conversation_id}")
def get_conversation_messages(
    conversation_id: str,
    service=Depends(conversation_service),
    user=Depends(get_current_user)
):
    try:
        return service.get_conversation_messages(conversation_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: str,
    service=Depends(conversation_service),
    user=Depends(get_current_user)
):
    try:
        service.delete_conversation(conversation_id, user["id"])
        return {"message": "Conversation supprimée avec succès"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
