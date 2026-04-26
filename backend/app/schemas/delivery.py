"""
app/schemas/delivery.py
────────────────────────
Schemas Pydantic para el módulo de entregas.

Estructura:
  ├─ Items
  │   ├─ DeliveryItemCreate
  │   ├─ DeliveryItemUpdate
  │   └─ DeliveryItemRead
  ├─ Address
  │   ├─ AddressCreate
  │   └─ AddressRead
  ├─ Delivery
  │   ├─ DeliveryCreate      — Crear entrega (con ítems embebidos)
  │   ├─ DeliveryUpdate      — Actualizar campos opcionales
  │   ├─ DeliveryStatusUpdate — Solo cambio de estado (endpoint dedicado)
  │   ├─ DeliveryRead        — Respuesta completa
  │   ├─ DeliveryListItem    — Respuesta reducida para listados
  │   └─ DeliveryPage        — Paginación
  └─ Filters
      └─ DeliveryFilters     — Query params de búsqueda
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional, Annotated, Any
from uuid import UUID

from pydantic import (
    BaseModel, ConfigDict, Field,
    field_validator, model_validator,
)

from app.models.delivery import DeliveryStatus
from app.schemas.user import UserShort
from app.schemas.proof import ProofRead


# ══════════════════════════════════════════════
#  DELIVERY ITEMS
# ══════════════════════════════════════════════
class DeliveryItemCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=200, examples=["Laptop Dell XPS"])
    description: Optional[str] = None
    sku: Optional[str] = Field(None, max_length=100)
    quantity: Decimal = Field(..., gt=0, examples=[1])
    unit: str = Field("unidad", max_length=30)
    weight_kg: Optional[Decimal] = Field(None, ge=0)
    declared_value: Optional[Decimal] = Field(None, ge=0)
    is_fragile: bool = False
    requires_refrigeration: bool = False

    @field_validator("quantity")
    @classmethod
    def quantity_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")
        return v


class DeliveryItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=200)
    description: Optional[str] = None
    sku: Optional[str] = None
    quantity: Optional[Decimal] = Field(None, gt=0)
    unit: Optional[str] = None
    weight_kg: Optional[Decimal] = Field(None, ge=0)
    declared_value: Optional[Decimal] = Field(None, ge=0)
    is_fragile: Optional[bool] = None
    requires_refrigeration: Optional[bool] = None


class DeliveryItemRead(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    sku: Optional[str]
    quantity: Decimal
    unit: str
    weight_kg: Optional[Decimal]
    declared_value: Optional[Decimal]
    is_fragile: bool
    requires_refrigeration: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ══════════════════════════════════════════════
#  ADDRESS
# ══════════════════════════════════════════════
class AddressCreate(BaseModel):
    street: str = Field(..., min_length=3, max_length=255)
    city: str = Field(..., min_length=2, max_length=100)
    state: Optional[str] = None
    country: str = Field("Colombia", max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)

    model_config = ConfigDict(from_attributes=True)


class AddressRead(AddressCreate):
    id: UUID
    lat: Optional[float] = None
    lng: Optional[float] = None


# ══════════════════════════════════════════════
#  DELIVERY — CREATE
# ══════════════════════════════════════════════
class DeliveryCreate(BaseModel):
    tracking_no: str = Field(
        ..., min_length=3, max_length=60,
        pattern=r"^[A-Za-z0-9\-_]+$",
        examples=["TRK-2026-001"],
        description="Código único de seguimiento. Solo letras, números, guiones y underscores.",
    )
    recipient_name: str = Field(..., min_length=2, max_length=150)
    recipient_phone: Optional[str] = Field(None, max_length=30)
    recipient_email: Optional[str] = Field(None, max_length=255)
    scheduled_at: datetime
    priority: int = Field(3, ge=1, le=5, description="1=Urgente, 5=Mínima")
    notes: Optional[str] = None
    driver_id: Optional[UUID] = None
    address: AddressCreate
    items: list[DeliveryItemCreate] = Field(
        default_factory=list,
        description="Lista de ítems de la entrega",
    )

    @field_validator("scheduled_at")
    @classmethod
    def scheduled_in_future(cls, v: datetime) -> datetime:
        if v < datetime.utcnow():
            raise ValueError("La fecha programada debe ser futura")
        return v

    @field_validator("tracking_no")
    @classmethod
    def tracking_uppercase(cls, v: str) -> str:
        return v.strip().upper()


# ══════════════════════════════════════════════
#  DELIVERY — UPDATE (campos opcionales)
# ══════════════════════════════════════════════
class DeliveryUpdate(BaseModel):
    recipient_name: Optional[str] = Field(None, min_length=2, max_length=150)
    recipient_phone: Optional[str] = None
    recipient_email: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None
    driver_id: Optional[UUID] = None
    failure_reason: Optional[str] = None


# ══════════════════════════════════════════════
#  DELIVERY — CAMBIO DE ESTADO (endpoint dedicado)
# ══════════════════════════════════════════════
class DeliveryStatusUpdate(BaseModel):
    """
    Endpoint dedicado para cambios de estado.
    Mantiene el principio de responsabilidad única.
    """
    status: DeliveryStatus
    failure_reason: Optional[str] = Field(
        None,
        description="Obligatorio cuando el nuevo estado es FAILED",
    )

    @model_validator(mode="after")
    def failure_reason_required_on_failed(self) -> "DeliveryStatusUpdate":
        if self.status == DeliveryStatus.FAILED and not self.failure_reason:
            raise ValueError("El motivo del fallo es obligatorio cuando el estado es FAILED")
        return self


# ══════════════════════════════════════════════
#  DELIVERY — READ (respuesta completa)
# ══════════════════════════════════════════════
class DeliveryRead(BaseModel):
    id: UUID
    tracking_no: str
    status: DeliveryStatus
    priority: int
    recipient_name: str
    recipient_phone: Optional[str]
    recipient_email: Optional[str]
    scheduled_at: datetime
    started_at: Optional[datetime]
    delivered_at: Optional[datetime]
    failed_at: Optional[datetime]
    failure_reason: Optional[str]
    notes: Optional[str]
    driver: Optional[UserShort]
    address: Optional[AddressRead]
    items: list[DeliveryItemRead] = []
    proofs: list[ProofRead] = []
    custom_fields: dict[str, Any] = {}
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class DeliveryListItem(BaseModel):
    """Versión reducida para listados — minimiza payload."""
    id: UUID
    tracking_no: str
    status: DeliveryStatus
    priority: int
    recipient_name: str
    scheduled_at: datetime
    driver: Optional[UserShort]
    city: Optional[str] = None       # Desnormalizado desde address
    total_items: int = 0

    model_config = ConfigDict(from_attributes=True)


# ══════════════════════════════════════════════
#  PAGINACIÓN
# ══════════════════════════════════════════════
class DeliveryPage(BaseModel):
    items: list[DeliveryListItem]
    total: int
    page: int
    size: int
    pages: int


# ══════════════════════════════════════════════
#  FILTROS (query params)
# ══════════════════════════════════════════════
class DeliveryFilters(BaseModel):
    """Filtros disponibles para GET /api/v1/deliveries."""
    status: Optional[DeliveryStatus] = None
    driver_id: Optional[UUID] = None
    city: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    # Rango de fechas
    scheduled_from: Optional[datetime] = None
    scheduled_to: Optional[datetime] = None
    created_from: Optional[datetime] = None
    created_to: Optional[datetime] = None
    # Búsqueda de texto
    search: Optional[str] = Field(None, description="Busca en tracking_no, recipient_name")
    # Paginación
    page: int = Field(1, ge=1)
    size: int = Field(20, ge=1, le=100)
    # Ordenamiento
    order_by: str = Field("created_at", description="Campo de ordenamiento")
    order_dir: str = Field("desc", pattern="^(asc|desc)$")


# ══════════════════════════════════════════════
#  DELIVERY — COMPLETE (con firma y GPS)
# ══════════════════════════════════════════════
class DeliveryCompleteRequest(BaseModel):
    """
    Payload para finalizar una entrega.
    Requiere firma en base64 y ubicación GPS.
    """
    actual_receiver_name: str = Field(..., min_length=2, max_length=150)
    signature_base64: str = Field(..., description="Firma en formato base64")
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    notes: Optional[str] = None

