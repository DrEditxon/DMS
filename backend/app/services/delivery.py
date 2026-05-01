from typing import List, Optional
from app.repositories.delivery import delivery_repo
from app.schemas.delivery import DeliveryCreate, DeliveryUpdate, DeliveryFilter, DeliveryStatus
from app.schemas.auth import UserResponse, UserRole
from fastapi import HTTPException
from app.core.websocket import manager
from app.repositories.notifications import notification_repo

class DeliveryService:
    async def create_delivery(self, delivery_in: DeliveryCreate, current_user: UserResponse):
        # Solo Admin puede crear
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        
        delivery = delivery_repo.create(delivery_in, dispatcher_id=current_user.id)
        
        # Guardar notificación persistente
        notification_repo.create_notification(
            user_id=current_user.id, # O al driver asignado
            title="Nueva Entrega",
            message=f"Se ha creado la entrega {delivery['tracking_number']}"
        )

        # Notificar en tiempo real
        await manager.broadcast({
            "type": "NEW_DELIVERY",
            "message": f"Nueva entrega creada: {delivery['tracking_number']}",
            "data": delivery
        })
        
        return delivery

    async def list_deliveries(self, filters: DeliveryFilter, current_user: UserResponse):
        # Admin ve todo, Operador solo lo suyo
        driver_id = None
        if current_user.role == UserRole.OPERATOR:
            driver_id = current_user.id
            
        return delivery_repo.get_multi(filters, driver_id=driver_id)

    def update_status(self, delivery_id: str, status_in: DeliveryStatus, current_user: UserResponse):
        # Lógica de transición de estados
        # Ejemplo: pending -> in_progress -> delivered
        # Aquí se podrían añadir validaciones más complejas
        update_data = DeliveryUpdate(status=status_in)
        return delivery_repo.update(delivery_id, update_data)

    def delete_delivery(self, delivery_id: str, current_user: UserResponse):
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return delivery_repo.delete(delivery_id)

delivery_service = DeliveryService()
