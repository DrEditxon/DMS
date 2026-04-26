"""
app/services/delivery_item_service.py
───────────────────────────────────────
Servicio dedicado a la lógica de negocio de delivery_items.

Responsabilidades:
  - Validaciones de dominio específicas de ítems
  - Orquestación entre item_repo y delivery_repo
  - Operaciones CRUD individuales y bulk
  - Cálculo de resumen/estadísticas
  - Control de acceso a nivel de ítem

Contratos de acceso:
  Crear ítem   → ADMIN, OPERATOR
  Leer ítems   → Todos los autenticados (con restricción de entrega)
  Actualizar   → ADMIN, OPERATOR
  Eliminar     → ADMIN
  Bulk replace → ADMIN
"""
from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.delivery import Delivery, DeliveryStatus
from app.models.delivery_item import DeliveryItem
from app.models.user import User, UserRole
from app.repositories.delivery_item_repository import item_repo
from app.repositories.delivery_repository import delivery_repo
from app.schemas.delivery import DeliveryItemCreate, DeliveryItemRead, DeliveryItemUpdate
from app.schemas.item import (
    ItemBulkCreate, ItemBulkResult, ItemFilters, ItemPage, ItemSummary,
)


# ══════════════════════════════════════════════════════════
#  HELPERS PRIVADOS
# ══════════════════════════════════════════════════════════
def _get_delivery_or_404(db: Session, delivery_id: uuid.UUID) -> Delivery:
    delivery = delivery_repo.get_with_relations(db, delivery_id)
    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Entrega {delivery_id} no encontrada",
        )
    return delivery


def _get_item_or_404(
    db: Session,
    delivery_id: uuid.UUID,
    item_id: uuid.UUID,
) -> DeliveryItem:
    item = item_repo.get_one(db, delivery_id, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ítem {item_id} no encontrado en la entrega {delivery_id}",
        )
    return item


def _assert_editable(delivery: Delivery) -> None:
    """Una entrega en estado final no acepta cambios en sus ítems."""
    final = {DeliveryStatus.DELIVERED, DeliveryStatus.CANCELLED, DeliveryStatus.FAILED}
    if delivery.status in final:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"No se pueden modificar ítems de una entrega en estado {delivery.status.value}",
        )


def _assert_role(actor: User, *roles: UserRole) -> None:
    if actor.role not in roles:
        allowed = ", ".join(r.value for r in roles)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Roles requeridos: {allowed}",
        )


def _assert_access(actor: User, delivery: Delivery) -> None:
    """DRIVER/OPERATOR solo pueden leer ítems de sus propias entregas."""
    if actor.role in (UserRole.ADMIN, UserRole.VIEWER):
        return
    if str(delivery.driver_id) != str(actor.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a los ítems de esta entrega",
        )


def _build_item(delivery_id: uuid.UUID, payload: DeliveryItemCreate) -> DeliveryItem:
    return DeliveryItem(
        delivery_id=delivery_id,
        name=payload.name,
        description=payload.description,
        sku=payload.sku,
        quantity=payload.quantity,
        unit=payload.unit,
        weight_kg=payload.weight_kg,
        declared_value=payload.declared_value,
        is_fragile=payload.is_fragile,
        requires_refrigeration=payload.requires_refrigeration,
    )


def _validate_no_sku_conflict(
    db: Session,
    delivery_id: uuid.UUID,
    sku: Optional[str],
    exclude_item_id: Optional[uuid.UUID] = None,
) -> None:
    """Garantiza que el SKU no esté duplicado dentro de la misma entrega."""
    if not sku:
        return
    existing = item_repo.get_by_sku(db, delivery_id, sku)
    if existing and (exclude_item_id is None or existing.id != exclude_item_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El SKU '{sku}' ya existe en esta entrega",
        )


# ══════════════════════════════════════════════════════════
#  CREAR — Un solo ítem
# ══════════════════════════════════════════════════════════
def create_item(
    db: Session,
    delivery_id: uuid.UUID,
    payload: DeliveryItemCreate,
    actor: User,
) -> DeliveryItem:
    """
    Añade un ítem a una entrega existente.

    Validaciones:
    - Entrega existe y no está en estado final
    - SKU único dentro de la entrega
    - Cantidad > 0 (validado en schema)
    """
    _assert_role(actor, UserRole.ADMIN, UserRole.OPERATOR)
    delivery = _get_delivery_or_404(db, delivery_id)
    _assert_editable(delivery)
    _validate_no_sku_conflict(db, delivery_id, payload.sku)

    item = _build_item(delivery_id, payload)
    return item_repo.create_one(db, item)


# ══════════════════════════════════════════════════════════
#  LISTAR — Con filtros y paginación
# ══════════════════════════════════════════════════════════
def list_items(
    db: Session,
    delivery_id: uuid.UUID,
    filters: ItemFilters,
    actor: User,
) -> ItemPage:
    """
    Listado paginado de ítems de una entrega con filtros opcionales.
    Cualquier usuario autenticado puede leer (con restricción de entrega).
    """
    delivery = _get_delivery_or_404(db, delivery_id)
    _assert_access(actor, delivery)

    result = item_repo.get_by_delivery_paginated(db, delivery_id, filters)
    return ItemPage(**result)


# ══════════════════════════════════════════════════════════
#  OBTENER — Un ítem
# ══════════════════════════════════════════════════════════
def get_item(
    db: Session,
    delivery_id: uuid.UUID,
    item_id: uuid.UUID,
    actor: User,
) -> DeliveryItem:
    delivery = _get_delivery_or_404(db, delivery_id)
    _assert_access(actor, delivery)
    return _get_item_or_404(db, delivery_id, item_id)


# ══════════════════════════════════════════════════════════
#  ACTUALIZAR — Un ítem
# ══════════════════════════════════════════════════════════
def update_item(
    db: Session,
    delivery_id: uuid.UUID,
    item_id: uuid.UUID,
    payload: DeliveryItemUpdate,
    actor: User,
) -> DeliveryItem:
    """
    Actualiza campos del ítem.
    Si cambia el SKU, valida que no exista otro con ese SKU en la misma entrega.
    """
    _assert_role(actor, UserRole.ADMIN, UserRole.OPERATOR)
    delivery = _get_delivery_or_404(db, delivery_id)
    _assert_editable(delivery)
    item = _get_item_or_404(db, delivery_id, item_id)

    data = payload.model_dump(exclude_unset=True)

    # Validar SKU solo si está siendo cambiado
    if "sku" in data:
        _validate_no_sku_conflict(db, delivery_id, data["sku"], exclude_item_id=item_id)

    for field, value in data.items():
        setattr(item, field, value)

    return item_repo.update_one(db, item)


# ══════════════════════════════════════════════════════════
#  ELIMINAR — Un ítem
# ══════════════════════════════════════════════════════════
def delete_item(
    db: Session,
    delivery_id: uuid.UUID,
    item_id: uuid.UUID,
    actor: User,
) -> dict:
    """
    Elimina permanentemente un ítem.
    Solo ADMIN. La entrega no debe estar en estado final.
    """
    _assert_role(actor, UserRole.ADMIN)
    delivery = _get_delivery_or_404(db, delivery_id)
    _assert_editable(delivery)
    item = _get_item_or_404(db, delivery_id, item_id)

    name_backup = item.name
    item_repo.delete_one(db, item)
    return {"message": f"Ítem '{name_backup}' eliminado de la entrega"}


# ══════════════════════════════════════════════════════════
#  BULK REPLACE — Reemplazar todos los ítems
# ══════════════════════════════════════════════════════════
def bulk_replace_items(
    db: Session,
    delivery_id: uuid.UUID,
    payload: ItemBulkCreate,
    actor: User,
) -> ItemBulkResult:
    """
    Reemplaza (o agrega) múltiples ítems en una sola operación atómica.

    Si `replace_all=True`:
      1. Elimina todos los ítems existentes
      2. Inserta los nuevos en bulk

    Si `replace_all=False`:
      - Solo inserta (append) sin eliminar los anteriores

    Validaciones cross-item:
      - No SKUs duplicados en el batch (validado en schema)
      - No SKU en conflicto con los ítems existentes (si !replace_all)
    """
    _assert_role(actor, UserRole.ADMIN)
    delivery = _get_delivery_or_404(db, delivery_id)
    _assert_editable(delivery)

    # Si !replace_all, validar conflictos de SKU con los existentes
    if not payload.replace_all:
        existing_skus = {
            i.sku for i in item_repo.get_by_delivery(db, delivery_id) if i.sku
        }
        for new_item in payload.items:
            if new_item.sku and new_item.sku in existing_skus:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"El SKU '{new_item.sku}' ya existe en la entrega (usa replace_all=true para reemplazar)",
                )

    deleted_count = 0
    if payload.replace_all:
        deleted_count = item_repo.delete_all_by_delivery(db, delivery_id)

    new_items = [_build_item(delivery_id, i) for i in payload.items]
    created   = item_repo.create_bulk(db, new_items)

    return ItemBulkResult(
        delivery_id=delivery_id,
        deleted_count=deleted_count,
        created_count=len(created),
        items=[DeliveryItemRead.model_validate(i) for i in created],
    )


# ══════════════════════════════════════════════════════════
#  SUMMARY — Estadísticas de ítems
# ══════════════════════════════════════════════════════════
def get_summary(
    db: Session,
    delivery_id: uuid.UUID,
    actor: User,
) -> ItemSummary:
    """
    Retorna estadísticas agregadas sobre los ítems de la entrega.
    Calculadas directamente en SQL para máximo rendimiento.
    """
    delivery = _get_delivery_or_404(db, delivery_id)
    _assert_access(actor, delivery)

    agg  = item_repo.get_summary_data(db, delivery_id)
    units = item_repo.get_units_breakdown(db, delivery_id)
    all_items = item_repo.get_by_delivery(db, delivery_id)

    return ItemSummary(
        delivery_id=delivery_id,
        total_items=agg["total_items"],
        total_quantity=agg["total_quantity"],
        total_weight_kg=agg["total_weight_kg"],
        total_declared_value=agg["total_declared_value"],
        fragile_count=agg["fragile_count"],
        refrigerated_count=agg["refrigerated_count"],
        units_breakdown=units,
        items=[DeliveryItemRead.model_validate(i) for i in all_items],
    )
