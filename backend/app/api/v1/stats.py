from fastapi import APIRouter, Depends
from app.api import deps
from app.repositories.stats import stats_repo

router = APIRouter()

@router.get("/")
def get_stats(current_user = Depends(deps.get_current_user)):
    return stats_repo.get_dashboard_stats()
