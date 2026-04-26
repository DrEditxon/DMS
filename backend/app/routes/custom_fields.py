"""
app/routes/custom_fields.py
─────────────────────────────
Endpoints para la administración de campos personalizados.
Permite a los administradores extender el modelo de datos.
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.middleware.auth_middleware import get_current_user, require_admin
from app.models.user import User
from app.schemas.custom_field import CustomFieldCreate, CustomFieldRead, CustomFieldValueUpdate
from app.services import custom_field_service

router = APIRouter()

@router.get("/", response_model=List[CustomFieldRead])
def list_custom_fields(
    applies_to: str = "delivery",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lista todos los campos activos para una entidad."""
    return custom_field_service.list_fields(db, applies_to=applies_to)

@router.post("/", response_model=CustomFieldRead, status_code=status.HTTP_201_CREATED)
def create_custom_field(
    payload: CustomFieldCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Crea un nuevo campo personalizado (Solo ADMIN)."""
    return custom_field_service.create_field(db, actor=admin, data=payload.model_dump())

@router.post("/values/{delivery_id}", status_code=status.HTTP_200_OK)
def set_delivery_custom_values(
    delivery_id: UUID,
    payload: CustomFieldValueUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Guarda los valores de campos personalizados para una entrega."""
    # Nota: Aquí se podrían añadir validaciones de permisos sobre la entrega
    custom_field_service.set_values(db, entity_id=delivery_id, values=payload.values, applies_to="delivery")
    return {"message": "Valores guardados correctamente"}

@router.get("/values/{delivery_id}")
def get_delivery_custom_values(
    delivery_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene los valores actuales de los campos personalizados de una entrega."""
    return custom_field_service.get_entity_values(db, entity_id=delivery_id, applies_to="delivery")
