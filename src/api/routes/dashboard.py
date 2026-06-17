from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import asyncio

from src.core.database import get_db
from src.repository.dashboard_repo import DashboardRepository
from src.security.jwt_handler import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard KPIs"])

from cachetools import TTLCache

# CACHÉ EN MEMORIA LRU: Evita saturación y memory leaks
# Máximo 100 consultas diferentes, expiran en 5 minutos (300 segundos)
dashboard_cache = TTLCache(maxsize=100, ttl=300)

async def _refresh_cache(db: Session, anio: int = None):
    """Obtiene KPIs, apoyándose en la caché LRU automáticamente"""
    cache_key = f"kpis_{anio if anio else 'todos'}"
    
    if cache_key in dashboard_cache:
        return dashboard_cache[cache_key], True
        
    repo = DashboardRepository(db)
    kpis = repo.get_kpis(anio=anio)
    
    dashboard_cache[cache_key] = kpis
    return kpis, False

@router.get("/kpis")
async def get_dashboard_kpis(
    anio: int = None,
    db: Session = Depends(get_db), 
    current_user: dict = Depends(get_current_user)
):
    """
    Retorna los KPIs centrales del Dashboard filtrados por año.
    Utiliza TTLCache para evitar sobrecargar PostGIS.
    """
    data, from_cache = await _refresh_cache(db, anio)
    return {
        "success": True,
        "from_cache": from_cache,
        "data": data
    }

@router.get("/mapa-geojson")
def get_mapa_geojson(db: Session = Depends(get_db)):
    """
    Retorna los puntos geográficos en tiempo real desde la BD PostGIS
    con coordenadas exactas (Lat/Lng) en lugar de una grilla agregada.
    """
    repo = DashboardRepository(db)
    puntos = repo.get_mapa_geojson()
    return {
        "success": True,
        "data": puntos
    }

@router.get("/analisis")
async def get_dashboard_analisis(
    anio: int = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Retorna datos de análisis avanzados formateados en DTOs para Recharts.
    """
    repo = DashboardRepository(db)
    data = repo.get_analisis(anio=anio)
    return {
        "success": True,
        "data": data
    }

@router.get("/stats-distrito/{distrito}")
async def get_stats_distrito(
    distrito: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Retorna las estadísticas delictivas para un distrito específico.
    """
    repo = DashboardRepository(db)
    data = repo.get_stats_distrito(distrito)
    return {
        "success": True,
        "data": data
    }
