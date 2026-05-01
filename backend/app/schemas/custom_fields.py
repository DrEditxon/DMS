from pydantic import BaseModel
from typing import List, Optional, Any
from enum import Enum

class CustomFieldType(str, Enum):
    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    SELECT = "select"

class CustomFieldCreate(BaseModel):
    name: str
    label: str
    data_type: CustomFieldType
    options: Optional[List[str]] = None # Para tipo SELECT

class CustomField(CustomFieldCreate):
    id: str

class CustomFieldValueCreate(BaseModel):
    field_id: str
    value: Any

class CustomFieldValueResponse(BaseModel):
    id: str
    field_id: str
    field_label: str
    value: Any
