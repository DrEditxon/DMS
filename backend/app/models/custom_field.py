"""
app/models/custom_field.py
──────────────────────────
Campos dinámicos configurables por administradores.
Permite extender los datos de entregas o ítems sin migraciones.
"""
import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, Enum as SAEnum, SmallInteger, JSON, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class FieldType(str, enum.Enum):
    TEXT    = "TEXT"
    NUMBER  = "NUMBER"
    DATE    = "DATE"
    BOOLEAN = "BOOLEAN"
    SELECT  = "SELECT"


class CustomField(Base):
    __tablename__ = "custom_fields"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    created_by  = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    name        = Column(String(100), nullable=False)   # snake_case id
    label       = Column(String(150), nullable=False)   # UI Label
    field_type  = Column(SAEnum(FieldType), nullable=False)
    is_required = Column(Boolean, default=False, nullable=False)
    is_active   = Column(Boolean, default=True, nullable=False)
    applies_to  = Column(String(50), default="delivery", nullable=False)  # "delivery" | "item"
    sort_order  = Column(SmallInteger, default=0, nullable=False)

    # Configuración extra (ej: opciones para SELECT)
    options     = Column(JSON, nullable=True)
    placeholder = Column(String(255), nullable=True)
    help_text   = Column(Text, nullable=True)

    created_at  = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at  = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    values = relationship("CustomFieldValue", back_populates="field", cascade="all, delete-orphan")


class CustomFieldValue(Base):
    __tablename__ = "custom_field_values"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    field_id    = Column(UUID(as_uuid=True), ForeignKey("custom_fields.id", ondelete="CASCADE"), nullable=False, index=True)

    # Polimorfismo manual: valor asociado a delivery o item
    delivery_id = Column(UUID(as_uuid=True), ForeignKey("deliveries.id", ondelete="CASCADE"), nullable=True, index=True)
    item_id     = Column(UUID(as_uuid=True), ForeignKey("delivery_items.id", ondelete="CASCADE"), nullable=True, index=True)

    # Valores tipados para facilitar filtros
    value_text    = Column(Text, nullable=True)
    value_number  = Column(Numeric, nullable=True)
    value_date    = Column(DateTime, nullable=True)
    value_boolean = Column(Boolean, nullable=True)

    created_at  = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at  = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    field    = relationship("CustomField", back_populates="values")
    delivery = relationship("Delivery")
    item     = relationship("DeliveryItem")

    def __repr__(self) -> str:
        return f"<CustomFieldValue field={self.field_id} val={self.value_text or self.value_number}>"
