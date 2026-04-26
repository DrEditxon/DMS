"""
app/schemas/custom_field.py
────────────────────────────
Schemas Pydantic para la gestión de campos dinámicos.
"""
from datetime import datetime
from typing import Optional, Any, List
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field
from app.models.custom_field import FieldType

class CustomFieldBase(BaseModel):
    name: str = Field(..., pattern="^[a-z0-9_]+$", description="ID interno (snake_case)")
    label: str
    field_type: FieldType
    is_required: bool = False
    is_active: bool = True
    applies_to: str = "delivery"
    sort_order: int = 0
    options: Optional[List[str]] = None  # Para el tipo SELECT
    placeholder: Optional[str] = None
    help_text: Optional[str] = None

class CustomFieldCreate(CustomFieldBase):
    pass

class CustomFieldRead(CustomFieldBase):
    id: UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class CustomFieldValueUpdate(BaseModel):
    """Asignación de valores: { "campo_slug": "valor" }"""
    values: dict[str, Any]
