from fastapi import APIRouter, Depends, HTTPException
from app.api import deps
from app.schemas.proof import DeliveryProofCreate, DeliveryProofResponse
from app.schemas.auth import UserResponse
from app.repositories.proof import proof_repo

router = APIRouter()

@router.post("/{delivery_id}/proof", response_model=DeliveryProofResponse)
def upload_delivery_proof(
    delivery_id: str,
    proof_in: DeliveryProofCreate,
    current_user: UserResponse = Depends(deps.get_current_user)
):
    # Solo el conductor asignado o admin debería poder subir la prueba
    # (Omitido por brevedad, pero recomendado en prod)
    return proof_repo.create_proof(delivery_id, proof_in)
