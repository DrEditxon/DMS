from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.api import deps
from app.schemas.delivery import DeliveryItem, DeliveryItemCreate
from app.schemas.auth import UserResponse
from app.services.delivery_item import item_service

router = APIRouter()

@router.post("/{delivery_id}/items", response_model=DeliveryItem)
def add_item_to_delivery(
    delivery_id: str,
    item_in: DeliveryItemCreate,
    current_user: UserResponse = Depends(deps.get_current_user)
):
    return item_service.add_item(delivery_id, item_in, current_user)

@router.patch("/items/{item_id}", response_model=DeliveryItem)
def update_item(
    item_id: str,
    item_in: dict, # Simplificado para el ejemplo
    current_user: UserResponse = Depends(deps.get_current_user)
):
    return item_service.update_item(item_id, item_in, current_user)

@router.delete("/items/{item_id}")
def delete_item(
    item_id: str,
    current_user: UserResponse = Depends(deps.get_current_user)
):
    return item_service.delete_item(item_id, current_user)
