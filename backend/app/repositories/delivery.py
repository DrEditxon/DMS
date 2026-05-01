from typing import List, Optional
from app.core.supabase import supabase
from app.schemas.delivery import DeliveryCreate, DeliveryUpdate, DeliveryFilter

class DeliveryRepository:
    def create(self, delivery_in: DeliveryCreate, dispatcher_id: str):
        # 1. Insertar Entrega
        delivery_data = delivery_in.dict(exclude={"items"})
        delivery_data["dispatcher_id"] = dispatcher_id
        
        result = supabase.table("deliveries").insert(delivery_data).execute()
        delivery = result.data[0]
        
        # 2. Insertar Ítems si existen
        if delivery_in.items:
            items_data = [
                {**item.dict(), "delivery_id": delivery["id"]} 
                for item in delivery_in.items
            ]
            supabase.table("delivery_items").insert(items_data).execute()
            
        return delivery

    def get_multi(self, filters: DeliveryFilter, driver_id: Optional[str] = None):
        query = supabase.table("deliveries").select("*, items:delivery_items(*)")
        
        if driver_id:
            query = query.eq("driver_id", driver_id)
        
        if filters.status:
            query = query.eq("status", filters.status)
            
        if filters.date_from:
            query = query.gte("created_at", filters.date_from.isoformat())
            
        if filters.date_to:
            query = query.lte("created_at", filters.date_to.isoformat())
            
        result = query.execute()
        return result.data

    def update(self, delivery_id: str, obj_in: DeliveryUpdate):
        result = supabase.table("deliveries").update(obj_in.dict(exclude_unset=True)).eq("id", delivery_id).execute()
        return result.data[0] if result.data else None

    def delete(self, delivery_id: str):
        result = supabase.table("deliveries").delete().eq("id", delivery_id).execute()
        return result.data

delivery_repo = DeliveryRepository()
