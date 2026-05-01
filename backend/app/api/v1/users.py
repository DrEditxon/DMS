from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.api import deps
from app.schemas.auth import UserResponse, UserRole
from app.repositories.user import user_repo, UserUpdate

router = APIRouter()

# Middleware de Admin para todas las rutas de este router
def admin_required(current_user: UserResponse = Depends(deps.get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can manage users")
    return current_user

@router.get("/", response_model=List[UserResponse])
def list_users(_ = Depends(admin_required)):
    return user_repo.get_all()

@router.patch("/{user_id}", response_model=UserResponse)
def update_user(user_id: str, user_in: UserUpdate, _ = Depends(admin_required)):
    return user_repo.update(user_id, user_in)

@router.delete("/{user_id}")
def delete_user(user_id: str, _ = Depends(admin_required)):
    return user_repo.delete(user_id)
