import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    action      = Column(String(100), nullable=False)   # e.g. "DELIVERY_CREATED"
    detail      = Column(Text, nullable=True)
    actor_id    = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    delivery_id = Column(UUID(as_uuid=True), ForeignKey("deliveries.id"), nullable=True)
    created_at  = Column(DateTime, default=datetime.utcnow)

    actor    = relationship("User", back_populates="audit_logs")
    delivery = relationship("Delivery", back_populates="logs")
