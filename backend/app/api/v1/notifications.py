from fastapi import APIRouter, Depends
from typing import List
from app.api import deps
from app.repositories.notifications import notification_repo, NotificationResponse
from app.schemas.auth import UserResponse

router = APIRouter()

@router.get("/", response_model=List[NotificationResponse])
def list_notifications(current_user: UserResponse = Depends(deps.get_current_user)):
    return notification_repo.get_user_notifications(current_user.id)

@router.patch("/{notification_id}/read")
def mark_read(notification_id: str, current_user: UserResponse = Depends(deps.get_current_user)):
    return notification_repo.mark_as_read(notification_id)
