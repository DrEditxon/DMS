from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.api import deps
from app.schemas.custom_fields import CustomField, CustomFieldCreate, CustomFieldValueCreate
from app.schemas.auth import UserResponse, UserRole
from app.repositories.custom_fields import custom_field_repo

router = APIRouter()

@router.get("/", response_model=List[CustomField])
def list_fields(current_user: UserResponse = Depends(deps.get_current_user)):
    return custom_field_repo.get_all_fields()

@router.post("/", response_model=CustomField)
def create_field(
    field_in: CustomFieldCreate,
    current_user: UserResponse = Depends(deps.get_current_user)
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can create custom fields")
    return custom_field_repo.create_field(field_in)

@router.get("/{delivery_id}/values")
def get_delivery_custom_values(
    delivery_id: str,
    current_user: UserResponse = Depends(deps.get_current_user)
):
    return custom_field_repo.get_values(delivery_id)

@router.post("/{delivery_id}/values")
def save_delivery_custom_values(
    delivery_id: str,
    values_in: List[CustomFieldValueCreate],
    current_user: UserResponse = Depends(deps.get_current_user)
):
    return custom_field_repo.save_values(delivery_id, values_in)
