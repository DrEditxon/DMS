from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DeliveryProofCreate(BaseModel):
    signature_base64: str
    latitude: float
    longitude: float
    receiver_name: str

class DeliveryProofResponse(BaseModel):
    id: str
    delivery_id: str
    media_url: str
    receiver_name: str
    created_at: datetime

    class Config:
        from_attributes = True
