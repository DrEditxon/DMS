"""
app/routes/delivery_items.py
─────────────────────────────
Router dedicado a los ítems de entregas.
Prefijo completo: /api/v1/deliveries/{delivery_id}/items

Endpoints:
  GET    /                  Listar ítems (paginado + filtros)
  POST   /                  Crear un ítem
  GET    /summary           Estadísticas agregadas de ítems
  PUT    /bulk              Reemplazar todos los ítems (bulk)
  GET    /{item_id}         Obtener un ítem
  PUT    /{item_id}         Actualizar un ítem
  DELETE /{item_id}         Eliminar un ítem

Nota: este router se monta como sub-router de deliveries en main.py.
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth_middleware import get_current_user
from app.models.user import User
from app.schemas.delivery import DeliveryItemCreate, DeliveryItemRead, DeliveryItemUpdate
from app.schemas.item import (
    ItemBulkCreate, ItemBulkResult, ItemFilters, ItemPage, ItemSummary,
)
from app.services import delivery_item_service

router = APIRouter()


# ══════════════════════════════════════════════════════════
#  GET / — Listar ítems
# ══════════════════════════════════════════════════════════
@router.get(
    "/",
    response_model=ItemPage,
    summary="Listar ítems de una entrega",
    description=(
        "Retorna los ítems de la entrega con paginación y filtros.\n\n"
        "**Filtros disponibles:** `search` (nombre/SKU/descripción), `sku`, "
        "`is_fragile`, `requires_refrigeration`, rango de cantidad."
    ),
)
def list_items(
    delivery_id: UUID,
    search: Optional[str]  = Query(None, description="Busca en nombre, SKU y descripción"),
    sku: Optional[str]     = Query(None),
    is_fragile: Optional[bool]             = Query(None),
    requires_refrigeration: Optional[bool] = Query(None),
    min_quantity: Optional[float]          = Query(None, ge=0),
    max_quantity: Optional[float]          = Query(None, ge=0),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from decimal import Decimal
    filters = ItemFilters(
        search=search,
        sku=sku,
        is_fragile=is_fragile,
        requires_refrigeration=requires_refrigeration,
        min_quantity=Decimal(str(min_quantity)) if min_quantity is not None else None,
        max_quantity=Decimal(str(max_quantity)) if max_quantity is not None else None,
        page=page,
        size=size,
    )
    return delivery_item_service.list_items(db, delivery_id, filters, current_user)


# ══════════════════════════════════════════════════════════
#  POST / — Crear ítem
# ══════════════════════════════════════════════════════════
@router.post(
    "/",
    response_model=DeliveryItemRead,
    status_code=status.HTTP_201_CREATED,
    summary="Añadir ítem a entrega",
    description=(
        "Añade un único ítem a una entrega existente.\n\n"
        "**Rol requerido:** `ADMIN` o `OPERATOR`\n\n"
        "La entrega no debe estar en estado final (DELIVERED, FAILED, CANCELLED).\n"
        "El SKU debe ser único dentro de la misma entrega."
    ),
)
def create_item(
    delivery_id: UUID,
    payload: DeliveryItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delivery_item_service.create_item(db, delivery_id, payload, current_user)


# ══════════════════════════════════════════════════════════
#  GET /summary — Estadísticas agregadas
# ══════════════════════════════════════════════════════════
@router.get(
    "/summary",
    response_model=ItemSummary,
    summary="Resumen de ítems",
    description=(
        "Estadísticas calculadas sobre los ítems de la entrega:\n\n"
        "- Total de ítems y cantidad\n"
        "- Peso total declarado\n"
        "- Valor total declarado\n"
        "- Cantidad de ítems frágiles y refrigerados\n"
        "- Desglose por unidad de medida"
    ),
)
def get_summary(
    delivery_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delivery_item_service.get_summary(db, delivery_id, current_user)


# ══════════════════════════════════════════════════════════
#  PUT /bulk — Reemplazar todos los ítems
# ══════════════════════════════════════════════════════════
@router.put(
    "/bulk",
    response_model=ItemBulkResult,
    summary="Reemplazar ítems en bulk",
    description=(
        "Operación atómica para gestionar todos los ítems a la vez.\n\n"
        "**Rol requerido:** `ADMIN`\n\n"
        "Con `replace_all=true` (default):\n"
        "1. Elimina **todos** los ítems existentes\n"
        "2. Inserta los nuevos en una transacción\n\n"
        "Con `replace_all=false`:\n"
        "- Solo agrega los nuevos sin tocar los existentes\n\n"
        "**Límite:** máximo 100 ítems por operación.\n"
        "**Validación:** no se permiten SKUs duplicados en el mismo batch."
    ),
)
def bulk_replace(
    delivery_id: UUID,
    payload: ItemBulkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delivery_item_service.bulk_replace_items(db, delivery_id, payload, current_user)


# ══════════════════════════════════════════════════════════
#  GET /{item_id} — Obtener un ítem
# ══════════════════════════════════════════════════════════
@router.get(
    "/{item_id}",
    response_model=DeliveryItemRead,
    summary="Obtener ítem",
)
def get_item(
    delivery_id: UUID,
    item_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delivery_item_service.get_item(db, delivery_id, item_id, current_user)


# ══════════════════════════════════════════════════════════
#  PUT /{item_id} — Actualizar ítem
# ══════════════════════════════════════════════════════════
@router.put(
    "/{item_id}",
    response_model=DeliveryItemRead,
    summary="Actualizar ítem",
    description=(
        "Actualiza campos del ítem (todos opcionales — PATCH semántico).\n\n"
        "**Rol requerido:** `ADMIN` o `OPERATOR`\n\n"
        "Si se cambia el SKU, se valida que no exista otro ítem con ese SKU en la entrega."
    ),
)
def update_item(
    delivery_id: UUID,
    item_id: UUID,
    payload: DeliveryItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delivery_item_service.update_item(db, delivery_id, item_id, payload, current_user)


# ══════════════════════════════════════════════════════════
#  DELETE /{item_id} — Eliminar ítem
# ══════════════════════════════════════════════════════════
@router.delete(
    "/{item_id}",
    summary="Eliminar ítem",
    description=(
        "Elimina permanentemente un ítem.\n\n"
        "**Rol requerido:** `ADMIN`\n\n"
        "No se puede eliminar ítems de entregas en estado final."
    ),
)
def delete_item(
    delivery_id: UUID,
    item_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return delivery_item_service.delete_item(db, delivery_id, item_id, current_user)
