from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class NotificationResponse(BaseModel):
    id: str
    title: str
    message: str
    type: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Repository
from app.core.supabase import supabase

class NotificationRepository:
    def get_user_notifications(self, user_id: str, limit: int = 20):
        result = supabase.table("notifications")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .limit(limit)\
            .execute()
        return result.data

    def create_notification(self, user_id: str, title: str, message: str, n_type: str = "info"):
        data = {
            "user_id": user_id,
            "title": title,
            "message": message,
            "type": n_type
        }
        return supabase.table("notifications").insert(data).execute().data[0]

    def mark_as_read(self, notification_id: str):
        return supabase.table("notifications").update({"is_read": True}).eq("id", notification_id).execute().data

notification_repo = NotificationRepository()
