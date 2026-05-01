from app.core.supabase import supabase
from app.schemas.custom_fields import CustomFieldCreate, CustomFieldValueCreate

class CustomFieldRepository:
    def create_field(self, field_in: CustomFieldCreate):
        return supabase.table("custom_fields").insert(field_in.dict()).execute().data[0]

    def get_all_fields(self):
        return supabase.table("custom_fields").select("*").execute().data

    def save_values(self, entity_id: str, values: List[CustomFieldValueCreate]):
        data = [
            {**v.dict(), "entity_id": entity_id} 
            for v in values
        ]
        return supabase.table("custom_field_values").upsert(data, on_conflict="field_id,entity_id").execute().data

    def get_values(self, entity_id: str):
        # Join con custom_fields para traer los labels
        return supabase.table("custom_field_values").select("*, field:custom_fields(label)").eq("entity_id", entity_id).execute().data

custom_field_repo = CustomFieldRepository()
