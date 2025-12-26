from fastapi import APIRouter, Depends
from app.schemas.user import UserResponse
from app.dependencies.auth import get_token
from app.services.user_service import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("/me", response_model=UserResponse)
def read_current_user(user: dict = Depends(get_current_user)):
    return user
