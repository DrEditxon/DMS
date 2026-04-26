"""
app/models/delivery.py
───────────────────────
Modelo ORM principal de entregas.
Estado mapeado al flujo requerido:
  PENDING → IN_PROGRESS → DELIVERED
  (con paradas opcionales: ASSIGNED, FAILED, CANCELLED)
"""
import uuid
import enum
from datetime import datetime
from sqlalchemy import (
    Column, String, Float, SmallInteger,
    DateTime, ForeignKey, Enum as SAEnum, Text, Boolean,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class DeliveryStatus(str, enum.Enum):
    PENDING     = "PENDING"       # Creada, sin asignar
    ASSIGNED    = "ASSIGNED"      # Asignada a repartidor
    IN_PROGRESS = "IN_PROGRESS"   # En camino (≡ IN_TRANSIT — nombre requerido)
    DELIVERED   = "DELIVERED"     # Entregada exitosamente
    FAILED      = "FAILED"        # Falló la entrega
    CANCELLED   = "CANCELLED"     # Cancelada antes de iniciar


# Mapa de transiciones válidas (dominio de negocio)
VALID_TRANSITIONS: dict[DeliveryStatus, list[DeliveryStatus]] = {
    DeliveryStatus.PENDING:     [DeliveryStatus.ASSIGNED,    DeliveryStatus.CANCELLED],
    DeliveryStatus.ASSIGNED:    [DeliveryStatus.IN_PROGRESS, DeliveryStatus.CANCELLED],
    DeliveryStatus.IN_PROGRESS: [DeliveryStatus.DELIVERED,   DeliveryStatus.FAILED],
    DeliveryStatus.DELIVERED:   [],
    DeliveryStatus.FAILED:      [],
    DeliveryStatus.CANCELLED:   [],
}


class Delivery(Base):
    __tablename__ = "deliveries"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    tracking_no = Column(String(60), unique=True, index=True, nullable=False)
    status      = Column(SAEnum(DeliveryStatus), default=DeliveryStatus.PENDING, nullable=False, index=True)
    priority    = Column(SmallInteger, default=3, nullable=False)   # 1=urgente, 5=baja
    notes       = Column(Text, nullable=True)
    is_deleted  = Column(Boolean, default=False, nullable=False)    # Soft delete

    # Asignación
    driver_id   = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    created_by  = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Dirección (FK a tabla addresses)
    address_id  = Column(UUID(as_uuid=True), ForeignKey("addresses.id"), nullable=False)

    # Receptor
    recipient_name  = Column(String(150), nullable=False)
    recipient_phone = Column(String(30),  nullable=True)
    recipient_email = Column(String(255), nullable=True)
    actual_receiver_name = Column(String(150), nullable=True)  # El que firma


    # Tiempos
    scheduled_at = Column(DateTime, nullable=False, index=True)
    started_at   = Column(DateTime, nullable=True)   # IN_PROGRESS
    delivered_at = Column(DateTime, nullable=True)   # DELIVERED
    failed_at    = Column(DateTime, nullable=True)   # FAILED
    failure_reason = Column(Text, nullable=True)

    # Auditoría
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ── Relationships ─────────────────────────────────────────
    driver  = relationship("User", back_populates="deliveries", foreign_keys=[driver_id])
    address = relationship("Address")
    logs    = relationship("AuditLog", back_populates="delivery")
    items   = relationship("DeliveryItem", back_populates="delivery",
                           cascade="all, delete-orphan", lazy="selectin")
    proofs  = relationship("DeliveryProof", back_populates="delivery",
                           cascade="all, delete-orphan", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Delivery {self.tracking_no} [{self.status}]>"
