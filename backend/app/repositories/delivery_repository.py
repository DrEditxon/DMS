"""
app/repositories/delivery_repository.py
─────────────────────────────────────────
Acceso a datos de entregas.
Responsabilidades ÚNICAS:
  - Queries SQL vía SQLAlchemy
  - Paginación y filtros
  - Sin lógica de negocio
"""
from __future__ import annotations

import math
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import asc, desc, or_, and_, func
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.address import Address
from app.models.delivery import Delivery, DeliveryStatus
from app.models.delivery_item import DeliveryItem
from app.repositories.base_repository import BaseRepository
from app.schemas.delivery import DeliveryFilters


class DeliveryRepository(BaseRepository[Delivery]):
    def __init__(self):
        super().__init__(Delivery)

    # ─────────────────────────────────────────
    #  LECTURAS
    # ─────────────────────────────────────────
    def get_with_relations(self, db: Session, delivery_id: uuid.UUID) -> Optional[Delivery]:
        """Carga entrega con driver, address e ítems. Excluye soft-deleted."""
        return (
            db.query(Delivery)
            .options(
                joinedload(Delivery.driver),
                joinedload(Delivery.address),
                selectinload(Delivery.items),
            )
            .filter(Delivery.id == delivery_id, Delivery.is_deleted == False)
            .first()
        )

    def get_paginated(
        self,
        db: Session,
        filters: DeliveryFilters,
        restrict_to_driver_id: Optional[uuid.UUID] = None,
    ) -> dict:
        """
        Listado paginado con todos los filtros disponibles.
        Si `restrict_to_driver_id` está presente, solo se devuelven
        las entregas asignadas a ese driver (visibilidad OPERATOR).
        """
        query = (
            db.query(Delivery)
            .options(joinedload(Delivery.driver), joinedload(Delivery.address))
            .filter(Delivery.is_deleted == False)
        )

        # ── Visibilidad por rol ───────────────
        if restrict_to_driver_id:
            query = query.filter(Delivery.driver_id == restrict_to_driver_id)

        # ── Filtros ───────────────────────────
        if filters.status:
            query = query.filter(Delivery.status == filters.status)

        if filters.driver_id:
            query = query.filter(Delivery.driver_id == filters.driver_id)

        if filters.priority:
            query = query.filter(Delivery.priority == filters.priority)

        if filters.city:
            query = query.join(Address).filter(
                Address.city.ilike(f"%{filters.city}%")
            )

        if filters.scheduled_from:
            query = query.filter(Delivery.scheduled_at >= filters.scheduled_from)

        if filters.scheduled_to:
            query = query.filter(Delivery.scheduled_at <= filters.scheduled_to)

        if filters.created_from:
            query = query.filter(Delivery.created_at >= filters.created_from)

        if filters.created_to:
            query = query.filter(Delivery.created_at <= filters.created_to)

        if filters.search:
            term = f"%{filters.search.strip()}%"
            query = query.filter(
                or_(
                    Delivery.tracking_no.ilike(term),
                    Delivery.recipient_name.ilike(term),
                    Delivery.recipient_phone.ilike(term),
                )
            )

        # ── Ordenamiento ──────────────────────
        order_col = getattr(Delivery, filters.order_by, Delivery.created_at)
        order_fn  = asc if filters.order_dir == "asc" else desc
        query = query.order_by(order_fn(order_col))

        # ── Paginación ────────────────────────
        total = query.count()
        items = query.offset((filters.page - 1) * filters.size).limit(filters.size).all()

        return {
            "items": items,
            "total": total,
            "page": filters.page,
            "size": filters.size,
            "pages": max(1, math.ceil(total / filters.size)),
        }

    def get_by_tracking(self, db: Session, tracking_no: str) -> Optional[Delivery]:
        return (
            db.query(Delivery)
            .filter(Delivery.tracking_no == tracking_no, Delivery.is_deleted == False)
            .first()
        )

    # ─────────────────────────────────────────
    #  CREACIÓN CON ADDRESS E ÍTEMS
    # ─────────────────────────────────────────
    def create_full(
        self,
        db: Session,
        delivery: Delivery,
        address: Address,
        items: list[DeliveryItem],
    ) -> Delivery:
        """
        Inserta address, delivery e ítems en una sola transacción.
        Usa flush() para obtener IDs sin hacer commit aún.
        """
        db.add(address)
        db.flush()                          # Obtiene address.id

        delivery.address_id = address.id
        db.add(delivery)
        db.flush()                          # Obtiene delivery.id

        for item in items:
            item.delivery_id = delivery.id
            db.add(item)

        db.commit()
        db.refresh(delivery)
        return delivery

    # ─────────────────────────────────────────
    #  ITEMS
    # ─────────────────────────────────────────
    def get_item(
        self, db: Session, delivery_id: uuid.UUID, item_id: uuid.UUID
    ) -> Optional[DeliveryItem]:
        return (
            db.query(DeliveryItem)
            .filter(DeliveryItem.id == item_id, DeliveryItem.delivery_id == delivery_id)
            .first()
        )

    def delete_item(self, db: Session, item: DeliveryItem) -> None:
        db.delete(item)
        db.commit()

    def get_stats(
        self, 
        db: Session, 
        start_date: Optional[datetime] = None, 
        end_date: Optional[datetime] = None
    ) -> dict:
        """
        Calcula estadísticas agregadas opcionalmente filtradas por fecha.
        """
        query = db.query(Delivery).filter(Delivery.is_deleted == False)
        
        if start_date:
            query = query.filter(Delivery.created_at >= start_date)
        if end_date:
            query = query.filter(Delivery.created_at <= end_date)
            
        # Agrupar por estado
        results = (
            db.query(Delivery.status, func.count(Delivery.id))
            .filter(Delivery.is_deleted == False)
        )
        
        if start_date:
            results = results.filter(Delivery.created_at >= start_date)
        if end_date:
            results = results.filter(Delivery.created_at <= end_date)
            
        status_counts = dict(results.group_by(Delivery.status).all())
        
        total = sum(status_counts.values())
        completed = status_counts.get(DeliveryStatus.DELIVERED, 0)
        
        return {
            "total": total,
            "pending": status_counts.get(DeliveryStatus.PENDING, 0),
            "in_progress": status_counts.get(DeliveryStatus.IN_PROGRESS, 0),
            "delivered": completed,
            "failed": status_counts.get(DeliveryStatus.FAILED, 0),
            "success_rate": round((completed / total * 100), 2) if total > 0 else 0
        }


delivery_repo = DeliveryRepository()
