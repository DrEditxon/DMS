from typing import List, Optional
from app.core.supabase import supabase
from app.schemas.delivery import DeliveryItemCreate

class DeliveryItemRepository:
    def get_by_delivery(self, delivery_id: str):
        result = supabase.table("delivery_items").select("*").eq("delivery_id", delivery_id).execute()
        return result.data

    def create(self, delivery_id: str, item_in: DeliveryItemCreate):
        item_data = item_in.dict()
        item_data["delivery_id"] = delivery_id
        result = supabase.table("delivery_items").insert(item_data).execute()
        return result.data[0]

    def update(self, item_id: str, item_in: dict):
        result = supabase.table("delivery_items").update(item_in).eq("id", item_id).execute()
        return result.data[0] if result.data else None

    def delete(self, item_id: str):
        result = supabase.table("delivery_items").delete().eq("id", item_id).execute()
        return result.data

item_repo = DeliveryItemRepository()
