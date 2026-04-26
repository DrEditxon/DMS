from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import dashboard_service
from app.middleware.auth_middleware import require_admin
from app.models.user import User

router = APIRouter()


@router.get("/stats")
def get_stats(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """Métricas agregadas del sistema de entregas con filtro de fechas."""
    return dashboard_service.get_stats(db, start_date, end_date)
