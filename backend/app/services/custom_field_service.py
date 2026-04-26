"""
app/services/custom_field_service.py
─────────────────────────────────────
Gestión de campos personalizados y sus valores.
Implementa el patrón EAV para flexibilidad total.
"""
import uuid
from typing import List, Optional, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.custom_field import CustomField, CustomFieldValue, FieldType
from app.models.user import User, UserRole


def list_fields(db: Session, applies_to: Optional[str] = None) -> List[CustomField]:
    query = db.query(CustomField).filter(CustomField.is_active == True)
    if applies_to:
        query = query.filter(CustomField.applies_to == applies_to)
    return query.order_by(CustomField.sort_order.asc()).all()


def create_field(db: Session, actor: User, data: dict) -> CustomField:
    if actor.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo ADMIN puede crear campos")
    
    field = CustomField(**data, created_by=actor.id)
    db.add(field)
    db.commit()
    db.refresh(field)
    return field


def set_values(
    db: Session,
    entity_id: uuid.UUID,
    values: dict,
    applies_to: str = "delivery"
):
    """
    Guarda valores para campos personalizados de una entidad.
    values: {"campo_slug": valor}
    """
    fields = {f.name: f for f in list_fields(db, applies_to)}
    
    for slug, val in values.items():
        if slug not in fields:
            continue
            
        field = fields[slug]
        
        # Buscar valor existente o crear uno nuevo
        filter_args = {"field_id": field.id}
        if applies_to == "delivery":
            filter_args["delivery_id"] = entity_id
        else:
            filter_args["item_id"] = entity_id
            
        existing = db.query(CustomFieldValue).filter_by(**filter_args).first()
        
        if existing:
            obj = existing
        else:
            obj = CustomFieldValue(field_id=field.id, **filter_args)
            db.add(obj)

        # Asignar valor según tipo
        if field.field_type == FieldType.NUMBER:
            obj.value_number = val
        elif field.field_type == FieldType.DATE:
            obj.value_date = val
        elif field.field_type == FieldType.BOOLEAN:
            obj.value_boolean = val
        else:
            obj.value_text = str(val) if val is not None else None

    db.commit()


def get_entity_values(db: Session, entity_id: uuid.UUID, applies_to: str = "delivery") -> dict:
    filter_args = {"delivery_id": entity_id} if applies_to == "delivery" else {"item_id": entity_id}
    
    results = (
        db.query(CustomFieldValue)
        .join(CustomField)
        .filter_by(**filter_args)
        .all()
    )
    
    output = {}
    for res in results:
        field = res.field
        if field.field_type == FieldType.NUMBER:
            val = res.value_number
        elif field.field_type == FieldType.DATE:
            val = res.value_date
        elif field.field_type == FieldType.BOOLEAN:
            val = res.value_boolean
        else:
            val = res.value_text
        output[field.name] = val
    return output
