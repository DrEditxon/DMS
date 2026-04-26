"""
app/services/delivery_service.py
──────────────────────────────────
Lógica de negocio del módulo de entregas.

Responsabilidades:
  - Validaciones de dominio (tracking único, driver activo, transiciones)
  - Orquestación de repositorios
  - Geocodificación de dirección
  - Visibilidad de datos según rol
  - Auditoría de acciones

Regla de transiciones de estado:
  PENDING → ASSIGNED → IN_PROGRESS → DELIVERED
                              └──────────────→ FAILED
  PENDING/ASSIGNED → CANCELLED
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.address import Address
from app.models.audit_log import AuditLog
from app.models.delivery import Delivery, DeliveryStatus, VALID_TRANSITIONS
from app.models.delivery_item import DeliveryItem
from app.models.delivery_proof import DeliveryProof, ProofType
from app.models.user import User, UserRole
from app.repositories.delivery_repository import delivery_repo
from app.repositories.user_repository import user_repo
from app.schemas.delivery import (
    DeliveryCreate, DeliveryFilters, DeliveryItemCreate,
    DeliveryItemUpdate, DeliveryPage, DeliveryRead,
    DeliveryStatusUpdate, DeliveryUpdate, DeliveryCompleteRequest,
)
from app.utils.geocoding import geocode_address


# ══════════════════════════════════════════════════════════
#  CREATE
# ══════════════════════════════════════════════════════════
async def create_delivery(
    db: Session,
    payload: DeliveryCreate,
    actor: User,
) -> Delivery:
    """
    Crea una entrega completa con dirección e ítems en una transacción.

    Solo ADMIN puede crear entregas.
    Valida: tracking único, driver activo, fecha futura.
    Geocodifica la dirección automáticamente (Nominatim/OSM).
    """
    _assert_role(actor, UserRole.ADMIN)

    # ── Validaciones ──────────────────────────────────────
    if delivery_repo.get_by_tracking(db, payload.tracking_no):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El tracking '{payload.tracking_no}' ya existe",
        )

    if payload.driver_id:
        driver = user_repo.get_active_by_id(db, payload.driver_id)
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Repartidor no encontrado o inactivo",
            )

    # ── Geocodificación ───────────────────────────────────
    coords = await geocode_address(
        payload.address.street, payload.address.city, payload.address.country
    )

    # ── Construir entidades ───────────────────────────────
    address = Address(
        street=payload.address.street,
        city=payload.address.city,
        state=payload.address.state,
        country=payload.address.country,
        postal_code=payload.address.postal_code,
        lat=coords[0] if coords else None,
        lng=coords[1] if coords else None,
    )

    initial_status = DeliveryStatus.ASSIGNED if payload.driver_id else DeliveryStatus.PENDING

    delivery = Delivery(
        tracking_no=payload.tracking_no,
        recipient_name=payload.recipient_name,
        recipient_phone=payload.recipient_phone,
        recipient_email=payload.recipient_email,
        scheduled_at=payload.scheduled_at,
        priority=payload.priority,
        notes=payload.notes,
        driver_id=payload.driver_id,
        created_by=actor.id,
        status=initial_status,
    )

    items = [_build_item(i) for i in payload.items]

    created = delivery_repo.create_full(db, delivery, address, items)
    _audit(db, actor, "DELIVERY_CREATED", created.id, f"Tracking: {created.tracking_no}")

    return delivery_repo.get_with_relations(db, created.id)


# ══════════════════════════════════════════════════════════
#  LIST (con visibilidad por rol)
# ══════════════════════════════════════════════════════════
def list_deliveries(
    db: Session,
    filters: DeliveryFilters,
    actor: User,
) -> DeliveryPage:
    """
    Listado paginado con filtros.

    Visibilidad:
      - ADMIN    → todas las entregas
      - OPERATOR → solo las asignadas a él (como driver)
      - DRIVER   → solo las suyas
      - VIEWER   → todas (solo lectura)
    """
    restrict_driver_id: Optional[uuid.UUID] = None

    if actor.role == UserRole.OPERATOR:
        # El OPERATOR solo ve las entregas donde él es el driver asignado
        restrict_driver_id = actor.id

    elif actor.role == UserRole.DRIVER:
        restrict_driver_id = actor.id

    result = delivery_repo.get_paginated(
        db, filters=filters, restrict_to_driver_id=restrict_driver_id
    )

    # Enriquecer con total_items y city para DeliveryListItem
    enriched_items = []
    for d in result["items"]:
        item_dict = {
            "id":             d.id,
            "tracking_no":    d.tracking_no,
            "status":         d.status,
            "priority":       d.priority,
            "recipient_name": d.recipient_name,
            "scheduled_at":   d.scheduled_at,
            "driver":         d.driver,
            "city":           d.address.city if d.address else None,
            "total_items":    len(d.items) if hasattr(d, "items") else 0,
        }
        enriched_items.append(item_dict)

    return DeliveryPage(
        items=enriched_items,
        total=result["total"],
        page=result["page"],
        size=result["size"],
        pages=result["pages"],
    )


# ══════════════════════════════════════════════════════════
#  GET BY ID
# ══════════════════════════════════════════════════════════
def get_delivery(
    db: Session,
    delivery_id: uuid.UUID,
    actor: User,
) -> Delivery:
    """
    Retorna entrega completa (con ítems).
    DRIVER y OPERATOR solo pueden ver las que tienen asignadas.
    """
    delivery = delivery_repo.get_with_relations(db, delivery_id)
    if not delivery:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entrega no encontrada")

    _assert_ownership_or_privilege(actor, delivery)
    return delivery


# ══════════════════════════════════════════════════════════
#  UPDATE FIELDS
# ══════════════════════════════════════════════════════════
def update_delivery(
    db: Session,
    delivery_id: uuid.UUID,
    payload: DeliveryUpdate,
    actor: User,
) -> Delivery:
    """
    Actualiza campos editables (no el estado).
    Solo ADMIN puede cambiar driver_id.
    """
    _assert_role(actor, UserRole.ADMIN, UserRole.OPERATOR)
    delivery = _get_or_404(db, delivery_id)
    _assert_not_final(delivery)

    data = payload.model_dump(exclude_unset=True)

    # Solo ADMIN puede reasignar driver
    if "driver_id" in data and actor.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo ADMIN puede reasignar el repartidor",
        )

    if "driver_id" in data and data["driver_id"]:
        driver = user_repo.get_active_by_id(db, data["driver_id"])
        if not driver:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Repartidor no encontrado")

    for field, value in data.items():
        setattr(delivery, field, value)

    delivery_repo.update(db, delivery)
    _audit(db, actor, "DELIVERY_UPDATED", delivery.id)
    return delivery_repo.get_with_relations(db, delivery.id)


# ══════════════════════════════════════════════════════════
#  UPDATE STATUS (endpoint dedicado)
# ══════════════════════════════════════════════════════════
def change_status(
    db: Session,
    delivery_id: uuid.UUID,
    payload: DeliveryStatusUpdate,
    actor: User,
) -> Delivery:
    """
    Cambia el estado de la entrega validando la máquina de estados.

    Flujo principal (requerido):
      PENDING → IN_PROGRESS → DELIVERED

    Reglas de negocio:
      - ADMIN/OPERATOR pueden mover cualquier transición válida
      - DRIVER solo puede mover: IN_PROGRESS → DELIVERED / FAILED
      - El estado FAILED requiere failure_reason
      - Se registran timestamps automáticos por estado
    """
    delivery = _get_or_404(db, delivery_id)
    _assert_ownership_or_privilege(actor, delivery)

    new_status = payload.status
    current    = delivery.status

    # DRIVER solo puede ejecutar la última milla
    if actor.role == UserRole.DRIVER:
        allowed_for_driver = [DeliveryStatus.DELIVERED, DeliveryStatus.FAILED]
        if new_status not in allowed_for_driver:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"DRIVER solo puede marcar como DELIVERED o FAILED",
            )

    # Validar transición según la máquina de estados
    valid_next = VALID_TRANSITIONS.get(current, [])
    if new_status not in valid_next:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Transición inválida: {current.value} → {new_status.value}. "
                f"Permitidas: {[s.value for s in valid_next] or 'ninguna'}"
            ),
        )

    # Actualizar timestamps automáticos
    delivery.status = new_status
    now = datetime.utcnow()

    if new_status == DeliveryStatus.IN_PROGRESS:
        delivery.started_at = now

    elif new_status == DeliveryStatus.DELIVERED:
        delivery.delivered_at = now

    elif new_status in (DeliveryStatus.FAILED, DeliveryStatus.CANCELLED):
        delivery.failed_at = now
        if payload.failure_reason:
            delivery.failure_reason = payload.failure_reason

    delivery_repo.update(db, delivery)
    _audit(
        db, actor,
        f"STATUS_{new_status.value}",
        delivery.id,
        f"{current.value} → {new_status.value}",
    )
    return delivery_repo.get_with_relations(db, delivery.id)


# ══════════════════════════════════════════════════════════
#  COMPLETE DELIVERY (con firma y GPS)
# ══════════════════════════════════════════════════════════
def complete_delivery(
    db: Session,
    delivery_id: uuid.UUID,
    payload: DeliveryCompleteRequest,
    actor: User,
) -> Delivery:
    """
    Finaliza una entrega requiriendo firma y ubicación GPS.
    """
    delivery = _get_or_404(db, delivery_id)
    _assert_ownership_or_privilege(actor, delivery)

    if delivery.status != DeliveryStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se pueden completar entregas que estén 'En Progreso'",
        )

    # 1. Registrar evidencia (firma)
    # En un sistema real, aquí guardaríamos el base64 en S3 y obtendríamos un URL.
    # Para este flujo funcional, guardaremos el base64 truncado o un placeholder.
    proof = DeliveryProof(
        delivery_id=delivery.id,
        uploaded_by=actor.id,
        proof_type=ProofType.SIGNATURE,
        file_url=f"data:image/png;base64,{payload.signature_base64[:50]}...", # Placeholder
        file_name="signature.png",
        lat=payload.lat,
        lng=payload.lng,
        notes=payload.notes,
    )
    db.add(proof)

    # 2. Actualizar entrega
    delivery.status = DeliveryStatus.DELIVERED
    delivery.delivered_at = datetime.utcnow()
    delivery.actual_receiver_name = payload.actual_receiver_name

    db.commit()
    _audit(db, actor, "DELIVERY_COMPLETED", delivery.id, f"Firmado por: {payload.actual_receiver_name}")

    return delivery_repo.get_with_relations(db, delivery.id)



# ══════════════════════════════════════════════════════════
#  DELETE (soft delete)
# ══════════════════════════════════════════════════════════
def delete_delivery(
    db: Session,
    delivery_id: uuid.UUID,
    actor: User,
) -> dict:
    """
    Soft delete: marca is_deleted=True.
    Solo ADMIN puede eliminar.
    No se pueden eliminar entregas en estado DELIVERED.
    """
    _assert_role(actor, UserRole.ADMIN)
    delivery = _get_or_404(db, delivery_id)

    if delivery.status == DeliveryStatus.DELIVERED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar una entrega ya entregada",
        )

    delivery.is_deleted = True
    delivery_repo.update(db, delivery)
    _audit(db, actor, "DELIVERY_DELETED", delivery.id)
    return {"message": f"Entrega {delivery.tracking_no} eliminada correctamente"}


# ══════════════════════════════════════════════════════════
#  ITEMS — CRUD
# ══════════════════════════════════════════════════════════
def add_item(
    db: Session,
    delivery_id: uuid.UUID,
    payload: DeliveryItemCreate,
    actor: User,
) -> Delivery:
    """Añade un ítem a una entrega existente. Solo ADMIN/OPERATOR."""
    _assert_role(actor, UserRole.ADMIN, UserRole.OPERATOR)
    delivery = _get_or_404(db, delivery_id)
    _assert_not_final(delivery)

    item = _build_item(payload)
    item.delivery_id = delivery.id
    db.add(item)
    db.commit()
    _audit(db, actor, "ITEM_ADDED", delivery.id, payload.name)
    return delivery_repo.get_with_relations(db, delivery.id)


def update_item(
    db: Session,
    delivery_id: uuid.UUID,
    item_id: uuid.UUID,
    payload: DeliveryItemUpdate,
    actor: User,
) -> Delivery:
    """Actualiza un ítem. Solo ADMIN/OPERATOR."""
    _assert_role(actor, UserRole.ADMIN, UserRole.OPERATOR)
    delivery = _get_or_404(db, delivery_id)
    _assert_not_final(delivery)

    item = delivery_repo.get_item(db, delivery_id, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ítem no encontrado")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)

    db.commit()
    return delivery_repo.get_with_relations(db, delivery.id)


def delete_item(
    db: Session,
    delivery_id: uuid.UUID,
    item_id: uuid.UUID,
    actor: User,
) -> Delivery:
    """Elimina un ítem. Solo ADMIN."""
    _assert_role(actor, UserRole.ADMIN)
    delivery = _get_or_404(db, delivery_id)
    _assert_not_final(delivery)

    item = delivery_repo.get_item(db, delivery_id, item_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ítem no encontrado")

    delivery_repo.delete_item(db, item)
    _audit(db, actor, "ITEM_DELETED", delivery.id, str(item_id))
    return delivery_repo.get_with_relations(db, delivery.id)


# ══════════════════════════════════════════════════════════
#  HELPERS PRIVADOS
# ══════════════════════════════════════════════════════════
def _get_or_404(db: Session, delivery_id: uuid.UUID) -> Delivery:
    """Obtiene la entrega o lanza 404."""
    delivery = delivery_repo.get_with_relations(db, delivery_id)
    if not delivery:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entrega no encontrada")
    return delivery


def _assert_role(actor: User, *roles: UserRole) -> None:
    """Lanza 403 si el actor no tiene ninguno de los roles requeridos."""
    if actor.role not in roles:
        allowed = ", ".join(r.value for r in roles)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Acción restringida. Roles permitidos: {allowed}",
        )


def _assert_ownership_or_privilege(actor: User, delivery: Delivery) -> None:
    """DRIVER/OPERATOR solo puede operar sobre sus entregas asignadas."""
    if actor.role in (UserRole.ADMIN, UserRole.VIEWER):
        return
    if str(delivery.driver_id) != str(actor.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos sobre esta entrega",
        )


def _assert_not_final(delivery: Delivery) -> None:
    """Impide modificar entregas en estado final."""
    final = (DeliveryStatus.DELIVERED, DeliveryStatus.CANCELLED, DeliveryStatus.FAILED)
    if delivery.status in final:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"No se puede modificar una entrega con estado {delivery.status.value}",
        )


def _build_item(payload: DeliveryItemCreate) -> DeliveryItem:
    return DeliveryItem(
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


def _audit(
    db: Session, actor: User,
    action: str, delivery_id: uuid.UUID,
    detail: Optional[str] = None,
) -> None:
    log = AuditLog(actor_id=actor.id, delivery_id=delivery_id, action=action, detail=detail)
    db.add(log)
    db.commit()
