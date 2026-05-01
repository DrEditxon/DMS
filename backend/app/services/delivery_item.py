from typing import List
from app.repositories.delivery_item import item_repo
from app.schemas.delivery import DeliveryItemCreate
from app.schemas.auth import UserResponse, UserRole
from fastapi import HTTPException

class DeliveryItemService:
    def add_item(self, delivery_id: str, item_in: DeliveryItemCreate, current_user: UserResponse):
        # Aquí se podría validar si la entrega pertenece al usuario si es Operador
        return item_repo.create(delivery_id, item_in)

    def update_item(self, item_id: str, item_in: dict, current_user: UserResponse):
        return item_repo.update(item_id, item_in)

    def delete_item(self, item_id: str, current_user: UserResponse):
        return item_repo.delete(item_id)

item_service = DeliveryItemService()
