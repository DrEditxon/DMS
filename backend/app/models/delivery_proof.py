"""
app/models/delivery_proof.py
──────────────────────────────
Evidencias de entrega: fotos, firmas, QR, documentos.
Guarda la ubicación GPS al momento de la captura.
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum as SAEnum, Integer, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.database import Base


class ProofType(str, enum.Enum):
    PHOTO     = "PHOTO"
    SIGNATURE = "SIGNATURE"
    QR_CODE   = "QR_CODE"
    DOCUMENT  = "DOCUMENT"


class DeliveryProof(Base):
    __tablename__ = "delivery_proofs"

    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    delivery_id  = Column(UUID(as_uuid=True), ForeignKey("deliveries.id", ondelete="CASCADE"), nullable=False, index=True)
    uploaded_by  = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    proof_type   = Column(SAEnum(ProofType), nullable=False)
    file_url     = Column(String(255), nullable=False)   # S3/CDN URL
    file_name    = Column(String(255), nullable=True)
    mime_type    = Column(String(100), nullable=True)
    file_size    = Column(Integer, nullable=True)        # Bytes

    # Contexto de captura
    lat          = Column(Float, nullable=True)
    lng          = Column(Float, nullable=True)
    notes        = Column(Text, nullable=True)

    created_at   = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    delivery = relationship("Delivery", back_populates="proofs")
    uploader = relationship("User")

    def __repr__(self) -> str:
        return f"<DeliveryProof {self.proof_type} for {self.delivery_id}>"
