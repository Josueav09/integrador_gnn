from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import asyncio

from src.core.database import get_db
from src.repository.dashboard_repo import DashboardRepository
from src.security.jwt_handler import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard KPIs"])

# CACHÉ EN MEMORIA PARA EVITAR CUELLO DE BOTELLA POSTGIS
_CACHE = {
    "kpis": None,
    "last_updated": None
}
CACHE_TTL_MINUTES = 5

async def _refresh_cache(db: Session):
    """Actualiza el caché si expiró o está vacío"""
    global _CACHE
    now = datetime.now()
    
    if _CACHE["kpis"] is None or _CACHE["last_updated"] is None or \
       (now - _CACHE["last_updated"]) > timedelta(minutes=CACHE_TTL_MINUTES):
        
        # Simular retardo si es necesario o ejecutar asincrónicamente
        repo = DashboardRepository(db)
        # En producción con alta carga, esto se ejecutaría en un background task
        # o celery worker, pero este in-memory cache protege la DB de N peticiones simultáneas.
        kpis = repo.get_kpis()
        
        _CACHE["kpis"] = kpis
        _CACHE["last_updated"] = now
        
    return _CACHE["kpis"]

@router.get("/kpis")
async def get_dashboard_kpis(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """
    Retorna los KPIs centrales del Dashboard.
    Utiliza un caché en memoria de 5 minutos para evitar sobrecargar PostGIS.
    """
    data = await _refresh_cache(db)
    return {
        "success": True,
        "data": data,
        "cached_at": _CACHE["last_updated"].isoformat() if _CACHE["last_updated"] else None
    }
