from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from app.models.delivery import DeliveryStatus
from app.repositories.delivery_repository import delivery_repo
from app.repositories.user_repository import user_repo
from app.models.user import UserRole


def get_stats(
    db: Session, 
    start_date: Optional[datetime] = None, 
    end_date: Optional[datetime] = None
) -> dict:
    """
    Obtiene métricas para el dashboard principal con soporte de filtros temporales.
    """
    stats = delivery_repo.get_stats(db, start_date, end_date)
    
    # Añadir datos extra que no dependen del filtro de fechas (opcional)
    stats.update({
        "total_drivers": user_repo.count_by_role(db, UserRole.DRIVER),
        "active_drivers": len(user_repo.get_active_drivers(db)),
    })
    
    return stats
