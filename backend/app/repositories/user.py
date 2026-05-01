from app.core.supabase import supabase
from app.schemas.auth import UserRole
from pydantic import BaseModel
from typing import Optional

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None

class UserRepository:
    def get_all(self):
        result = supabase.table("profiles").select("*").execute()
        return result.data

    def update(self, user_id: str, obj_in: UserUpdate):
        result = supabase.table("profiles")\
            .update(obj_in.dict(exclude_unset=True))\
            .eq("id", user_id)\
            .execute()
        return result.data[0] if result.data else None

    def delete(self, user_id: str):
        # En Supabase, borrar el perfil usualmente implica borrar de auth.users
        # Por ahora solo borramos de profiles o desactivamos
        return supabase.table("profiles").delete().eq("id", user_id).execute().data

user_repo = UserRepository()
