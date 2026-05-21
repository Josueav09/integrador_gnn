from sqlalchemy.orm import Session
from sqlalchemy import func, text
from datetime import datetime, timedelta
from src.core.models import Delito, TipoDelito, Cuadrante

class DashboardRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_kpis(self):
        # Para demostración, calculamos las estadísticas de los últimos 30 días
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        # 1. Total de delitos (últimos 30 días)
        total_delitos = self.db.query(func.count(Delito.id_delito)).filter(
            Delito.fecha_delito >= thirty_days_ago
        ).scalar() or 0

        # 2. Distribución por tipo de delito
        crimes_by_type = self.db.query(
            TipoDelito.nombre_tipo_delito,
            func.count(Delito.id_delito).label('total')
        ).join(Delito, TipoDelito.id_tipo_delito == Delito.id_tipo_delito)\
         .filter(Delito.fecha_delito >= thirty_days_ago)\
         .group_by(TipoDelito.nombre_tipo_delito).all()
        
        distribution = [{"type": row.nombre_tipo_delito, "count": row.total} for row in crimes_by_type]

        # 3. Tendencia semanal (últimos 7 días)
        seven_days_ago = datetime.now() - timedelta(days=7)
        weekly_trend = self.db.query(
            Delito.fecha_delito,
            func.count(Delito.id_delito).label('total')
        ).filter(Delito.fecha_delito >= seven_days_ago)\
         .group_by(Delito.fecha_delito)\
         .order_by(Delito.fecha_delito).all()
         
        trend = [{"date": str(row.fecha_delito), "count": row.total} for row in weekly_trend]

        # 4. Zonas Críticas (Top 5 Cuadrantes con más delitos)
        top_zones = self.db.query(
            Cuadrante.nombre_cuadrante,
            func.count(Delito.id_delito).label('total')
        ).join(Delito, Cuadrante.id_cuadrante == Delito.id_cuadrante)\
         .filter(Delito.fecha_delito >= thirty_days_ago)\
         .group_by(Cuadrante.nombre_cuadrante)\
         .order_by(func.count(Delito.id_delito).desc())\
         .limit(5).all()
         
        zones = [{"zone": row.nombre_cuadrante, "count": row.total} for row in top_zones]

        return {
            "total_delitos_30d": total_delitos,
            "distribucion_tipos": distribution,
            "tendencia_7d": trend,
            "top_zonas": zones,
            "nivel_riesgo_global": "Alto" if total_delitos > 100 else ("Medio" if total_delitos > 50 else "Bajo")
        }
