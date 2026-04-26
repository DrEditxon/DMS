"""
app/repositories/delivery_item_repository.py
─────────────────────────────────────────────
Repositorio dedicado a delivery_items.

Responsabilidades ÚNICAS:
  - Queries SQL de ítems vía SQLAlchemy
  - Paginación y filtros de ítems
  - Operaciones bulk (eliminar todos, insertar lote)
  - Sin lógica de negocio

Separado de delivery_repository.py para cumplir SRP.
"""
from __future__ import annotations

import math
import uuid
from decimal import Decimal
from typing import Optional

from sqlalchemy import or_, asc, desc, func
from sqlalchemy.orm import Session

from app.models.delivery_item import DeliveryItem
from app.repositories.base_repository import BaseRepository
from app.schemas.item import ItemFilters


class DeliveryItemRepository(BaseRepository[DeliveryItem]):
    def __init__(self):
        super().__init__(DeliveryItem)

    # ─────────────────────────────────────────
    #  LECTURA
    # ─────────────────────────────────────────
    def get_by_delivery(
        self,
        db: Session,
        delivery_id: uuid.UUID,
    ) -> list[DeliveryItem]:
        """Todos los ítems de una entrega, ordenados por fecha de creación."""
        return (
            db.query(DeliveryItem)
            .filter(DeliveryItem.delivery_id == delivery_id)
            .order_by(asc(DeliveryItem.created_at))
            .all()
        )

    def get_by_delivery_paginated(
        self,
        db: Session,
        delivery_id: uuid.UUID,
        filters: ItemFilters,
    ) -> dict:
        """Listado paginado de ítems con filtros opcionales."""
        query = db.query(DeliveryItem).filter(
            DeliveryItem.delivery_id == delivery_id
        )

        # ── Filtros ───────────────────────────
        if filters.search:
            term = f"%{filters.search.strip()}%"
            query = query.filter(
                or_(
                    DeliveryItem.name.ilike(term),
                    DeliveryItem.sku.ilike(term),
                    DeliveryItem.description.ilike(term),
                )
            )

        if filters.sku:
            query = query.filter(DeliveryItem.sku == filters.sku)

        if filters.is_fragile is not None:
            query = query.filter(DeliveryItem.is_fragile == filters.is_fragile)

        if filters.requires_refrigeration is not None:
            query = query.filter(
                DeliveryItem.requires_refrigeration == filters.requires_refrigeration
            )

        if filters.min_quantity is not None:
            query = query.filter(DeliveryItem.quantity >= filters.min_quantity)

        if filters.max_quantity is not None:
            query = query.filter(DeliveryItem.quantity <= filters.max_quantity)

        # ── Paginación ────────────────────────
        total = query.count()
        items = (
            query.order_by(asc(DeliveryItem.created_at))
            .offset((filters.page - 1) * filters.size)
            .limit(filters.size)
            .all()
        )

        return {
            "items": items,
            "total": total,
            "page": filters.page,
            "size": filters.size,
            "pages": max(1, math.ceil(total / filters.size)),
        }

    def get_one(
        self,
        db: Session,
        delivery_id: uuid.UUID,
        item_id: uuid.UUID,
    ) -> Optional[DeliveryItem]:
        """Un ítem específico validando que pertenezca a la entrega."""
        return (
            db.query(DeliveryItem)
            .filter(
                DeliveryItem.id == item_id,
                DeliveryItem.delivery_id == delivery_id,
            )
            .first()
        )

    def get_by_sku(
        self,
        db: Session,
        delivery_id: uuid.UUID,
        sku: str,
    ) -> Optional[DeliveryItem]:
        """Busca ítem por SKU dentro de una entrega."""
        return (
            db.query(DeliveryItem)
            .filter(
                DeliveryItem.delivery_id == delivery_id,
                DeliveryItem.sku == sku,
            )
            .first()
        )

    # ─────────────────────────────────────────
    #  ESCRITURA
    # ─────────────────────────────────────────
    def create_one(self, db: Session, item: DeliveryItem) -> DeliveryItem:
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    def create_bulk(
        self,
        db: Session,
        items: list[DeliveryItem],
    ) -> list[DeliveryItem]:
        """
        Inserta múltiples ítems en una sola transacción.
        Usa add_all + flush para eficiencia.
        """
        db.add_all(items)
        db.flush()
        db.commit()
        for item in items:
            db.refresh(item)
        return items

    def update_one(self, db: Session, item: DeliveryItem) -> DeliveryItem:
        db.commit()
        db.refresh(item)
        return item

    def delete_one(self, db: Session, item: DeliveryItem) -> None:
        db.delete(item)
        db.commit()

    def delete_all_by_delivery(self, db: Session, delivery_id: uuid.UUID) -> int:
        """
        Elimina todos los ítems de una entrega.
        Retorna la cantidad de ítems eliminados.
        """
        count = (
            db.query(DeliveryItem)
            .filter(DeliveryItem.delivery_id == delivery_id)
            .delete(synchronize_session="fetch")
        )
        db.commit()
        return count

    # ─────────────────────────────────────────
    #  AGREGADOS / ESTADÍSTICAS
    # ─────────────────────────────────────────
    def get_summary_data(
        self, db: Session, delivery_id: uuid.UUID
    ) -> dict:
        """
        Devuelve estadísticas agregadas calculadas en SQL.
        Evita traer todos los ítems a Python solo para sumarlos.
        """
        row = (
            db.query(
                func.count(DeliveryItem.id).label("total_items"),
                func.sum(DeliveryItem.quantity).label("total_quantity"),
                func.sum(DeliveryItem.weight_kg).label("total_weight_kg"),
                func.sum(DeliveryItem.declared_value).label("total_declared_value"),
                func.sum(
                    func.cast(DeliveryItem.is_fragile, db.bind.dialect.NUMERIC
                              if hasattr(db.bind, "dialect") else __import__("sqlalchemy").Integer)
                ).label("fragile_count"),
                func.sum(
                    func.cast(DeliveryItem.requires_refrigeration, __import__("sqlalchemy").Integer)
                ).label("refrigerated_count"),
            )
            .filter(DeliveryItem.delivery_id == delivery_id)
            .one()
        )
        return {
            "total_items":          row.total_items or 0,
            "total_quantity":       row.total_quantity or Decimal(0),
            "total_weight_kg":      row.total_weight_kg,
            "total_declared_value": row.total_declared_value,
            "fragile_count":        int(row.fragile_count or 0),
            "refrigerated_count":   int(row.refrigerated_count or 0),
        }

    def get_units_breakdown(
        self, db: Session, delivery_id: uuid.UUID
    ) -> dict[str, Decimal]:
        """Devuelve suma de cantidad agrupada por unidad."""
        rows = (
            db.query(DeliveryItem.unit, func.sum(DeliveryItem.quantity))
            .filter(DeliveryItem.delivery_id == delivery_id)
            .group_by(DeliveryItem.unit)
            .all()
        )
        return {unit: qty for unit, qty in rows}

    def count_by_delivery(self, db: Session, delivery_id: uuid.UUID) -> int:
        return (
            db.query(DeliveryItem)
            .filter(DeliveryItem.delivery_id == delivery_id)
            .count()
        )


# Singleton
item_repo = DeliveryItemRepository()
