from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from app.api import deps
from app.schemas.delivery import Delivery, DeliveryCreate, DeliveryUpdate, DeliveryFilter, DeliveryStatus
from app.schemas.auth import UserResponse
from app.services.delivery import delivery_service

router = APIRouter()

@router.post("/", response_model=Delivery)
async def create_delivery(
    delivery_in: DeliveryCreate,
    current_user: UserResponse = Depends(deps.get_current_user)
):
    return await delivery_service.create_delivery(delivery_in, current_user)

@router.get("/", response_model=List[Delivery])
def list_deliveries(
    status: Optional[DeliveryStatus] = None,
    driver_id: Optional[str] = None,
    current_user: UserResponse = Depends(deps.get_current_user)
):
    filters = DeliveryFilter(status=status, driver_id=driver_id)
    return delivery_service.list_deliveries(filters, current_user)

@router.patch("/{delivery_id}/status", response_model=Delivery)
def update_delivery_status(
    delivery_id: str,
    status: DeliveryStatus,
    current_user: UserResponse = Depends(deps.get_current_user)
):
    return delivery_service.update_status(delivery_id, status, current_user)

@router.delete("/{delivery_id}")
def delete_delivery(
    delivery_id: str,
    current_user: UserResponse = Depends(deps.get_current_user)
):
    return delivery_service.delete_delivery(delivery_id, current_user)
