"""
app/schemas/proof.py
──────────────────────
Schemas Pydantic para evidencias de entrega.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from app.models.delivery_proof import ProofType

class ProofBase(BaseModel):
    proof_type: ProofType
    file_url: str
    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    notes: Optional[str] = None

class ProofCreate(ProofBase):
    pass

class ProofRead(ProofBase):
    id: UUID
    delivery_id: UUID
    uploaded_by: Optional[UUID]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
