"""
app/services/proof_service.py
──────────────────────────────
Gestión de evidencias de entrega.
Maneja el registro de fotos y firmas vinculadas a una entrega.
"""
import uuid
from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.delivery_proof import DeliveryProof, ProofType
from app.models.user import User
from app.repositories.delivery_repository import delivery_repo


def add_proof(
    db: Session,
    delivery_id: uuid.UUID,
    actor: User,
    data: dict
) -> DeliveryProof:
    """Registra una nueva evidencia."""
    delivery = delivery_repo.get(db, delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="Entrega no encontrada")
        
    proof = DeliveryProof(
        delivery_id=delivery_id,
        uploaded_by=actor.id,
        **data
    )
    db.add(proof)
    db.commit()
    db.refresh(proof)
    return proof


def get_delivery_proofs(db: Session, delivery_id: uuid.UUID) -> List[DeliveryProof]:
    return db.query(DeliveryProof).filter(DeliveryProof.delivery_id == delivery_id).all()
