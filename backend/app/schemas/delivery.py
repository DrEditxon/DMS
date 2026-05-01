from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from app.schemas.auth import UserRole
from enum import Enum

class DeliveryStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class DeliveryItemBase(BaseModel):
    description: str
    quantity: int = 1
    weight_kg: Optional[float] = None

class DeliveryItemCreate(DeliveryItemBase):
    pass

class DeliveryItem(DeliveryItemBase):
    id: str
    delivery_id: str

    class Config:
        from_attributes = True

class DeliveryBase(BaseModel):
    tracking_number: str
    customer_name: str
    address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    scheduled_at: Optional[datetime] = None
    notes: Optional[str] = None

class DeliveryCreate(DeliveryBase):
    items: List[DeliveryItemCreate] = []

class DeliveryUpdate(BaseModel):
    status: Optional[DeliveryStatus] = None
    driver_id: Optional[str] = None
    notes: Optional[str] = None

class Delivery(DeliveryBase):
    id: str
    status: DeliveryStatus
    driver_id: Optional[str] = None
    dispatcher_id: Optional[str] = None
    items: List[DeliveryItem] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DeliveryFilter(BaseModel):
    status: Optional[DeliveryStatus] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    driver_id: Optional[str] = None
