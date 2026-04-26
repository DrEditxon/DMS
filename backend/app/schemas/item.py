"""
app/schemas/item.py
────────────────────
Schemas Pydantic dedicados al módulo de delivery_items.

Separados de delivery.py para mantener responsabilidad única.
Los schemas base (DeliveryItemCreate, etc.) viven en delivery.py
y se reexportan aquí para completitud.

Extras que agrega este módulo:
  ├─ ItemBulkCreate      — Reemplazar todos los ítems de una entrega
  ├─ ItemBulkResult      — Respuesta a operaciones bulk
  ├─ ItemSummary         — Stats agregados de ítems en una entrega
  └─ ItemPage            — Listado paginado de ítems
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# Re-export de los schemas base para no duplicar
from app.schemas.delivery import (
    DeliveryItemCreate,
    DeliveryItemUpdate,
    DeliveryItemRead,
)

__all__ = [
    "DeliveryItemCreate",
    "DeliveryItemUpdate",
    "DeliveryItemRead",
    "ItemBulkCreate",
    "ItemBulkResult",
    "ItemSummary",
    "ItemPage",
    "ItemFilters",
]


# ══════════════════════════════════════════════
#  BULK — Reemplazar todos los ítems de una entrega
# ══════════════════════════════════════════════
class ItemBulkCreate(BaseModel):
    """
    Reemplaza TODOS los ítems de una entrega en una sola operación.
    Útil para edición completa desde el frontend.

    Si `replace_all=True` (default), elimina los ítems existentes
    antes de insertar los nuevos.
    """
    items: list[DeliveryItemCreate] = Field(
        ...,
        min_length=1,
        description="Lista de ítems. Mínimo 1 ítem requerido.",
    )
    replace_all: bool = Field(
        True,
        description="Si True, elimina los ítems previos antes de insertar.",
    )

    @model_validator(mode="after")
    def no_duplicate_skus(self) -> "ItemBulkCreate":
        """Valida que no haya SKUs duplicados dentro del mismo batch."""
        skus = [i.sku for i in self.items if i.sku]
        if len(skus) != len(set(skus)):
            raise ValueError("El batch contiene SKUs duplicados")
        return self

    @model_validator(mode="after")
    def max_items_limit(self) -> "ItemBulkCreate":
        if len(self.items) > 100:
            raise ValueError("No se pueden enviar más de 100 ítems en una sola operación")
        return self


# ══════════════════════════════════════════════
#  BULK RESULT — Respuesta de operaciones masivas
# ══════════════════════════════════════════════
class ItemBulkResult(BaseModel):
    """Respuesta a `PUT /{delivery_id}/items/bulk`."""
    delivery_id: UUID
    deleted_count: int
    created_count: int
    items: list[DeliveryItemRead]


# ══════════════════════════════════════════════
#  SUMMARY — Estadísticas agregadas de ítems
# ══════════════════════════════════════════════
class ItemSummary(BaseModel):
    """
    Estadísticas calculadas sobre los ítems de una entrega.
    Devuelta por `GET /{delivery_id}/items/summary`.
    """
    delivery_id: UUID
    total_items: int
    total_quantity: Decimal
    total_weight_kg: Optional[Decimal]
    total_declared_value: Optional[Decimal]
    fragile_count: int
    refrigerated_count: int
    units_breakdown: dict[str, Decimal]   # {"unidad": 3, "kg": 1.5}
    items: list[DeliveryItemRead]


# ══════════════════════════════════════════════
#  PAGINACIÓN DE ÍTEMS
# ══════════════════════════════════════════════
class ItemPage(BaseModel):
    items: list[DeliveryItemRead]
    total: int
    page: int
    size: int
    pages: int


# ══════════════════════════════════════════════
#  FILTROS
# ══════════════════════════════════════════════
class ItemFilters(BaseModel):
    """Query params para filtrar ítems de una entrega."""
    search: Optional[str] = Field(None, description="Busca en name, sku, description")
    sku: Optional[str] = None
    is_fragile: Optional[bool] = None
    requires_refrigeration: Optional[bool] = None
    min_quantity: Optional[Decimal] = Field(None, ge=0)
    max_quantity: Optional[Decimal] = Field(None, ge=0)
    page: int = Field(1, ge=1)
    size: int = Field(50, ge=1, le=200)
