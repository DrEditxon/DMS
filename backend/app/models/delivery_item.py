"""
app/models/delivery_item.py
────────────────────────────
Ítem / producto incluido en una entrega.
Relación: muchos ítems → una entrega (CASCADE delete).
"""
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Numeric, Boolean,
    SmallInteger, DateTime, ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class DeliveryItem(Base):
    __tablename__ = "delivery_items"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    delivery_id = Column(UUID(as_uuid=True), ForeignKey("deliveries.id", ondelete="CASCADE"), nullable=False, index=True)

    # Descripción
    name        = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    sku         = Column(String(100), nullable=True, index=True)

    # Cantidad / peso / valor
    quantity        = Column(Numeric(10, 2), nullable=False, default=1)
    unit            = Column(String(30), nullable=False, default="unidad")   # kg, caja, unidad...
    weight_kg       = Column(Numeric(8, 3), nullable=True)
    declared_value  = Column(Numeric(12, 2), nullable=True)                 # Para seguros

    # Flags logísticos
    is_fragile              = Column(Boolean, default=False, nullable=False)
    requires_refrigeration  = Column(Boolean, default=False, nullable=False)

    # Auditoría
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relación inversa
    delivery = relationship("Delivery", back_populates="items")

    def __repr__(self) -> str:
        return f"<DeliveryItem {self.sku or self.name} x{self.quantity}>"
