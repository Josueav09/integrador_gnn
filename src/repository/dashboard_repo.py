from sqlalchemy.orm import Session
from sqlalchemy import func, text
from datetime import datetime, timedelta
from src.core.models import Delito, TipoDelito, Cuadrante, Distrito

class DashboardRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_kpis(self, anio: int = None):
        # Filtro base
        if anio:
            filtro_fecha = func.extract('year', Delito.fecha_delito) == anio
        else:
            # Por defecto últimos 30 días si no hay año
            thirty_days_ago = datetime.now() - timedelta(days=30)
            filtro_fecha = Delito.fecha_delito >= thirty_days_ago

        # 1. Total de delitos
        total_delitos = self.db.query(func.count(Delito.id_delito)).filter(
            filtro_fecha
        ).scalar() or 0

        # 2. Distribución por tipo de delito
        crimes_by_type = self.db.query(
            TipoDelito.nombre_tipo_delito,
            func.count(Delito.id_delito).label('total')
        ).join(Delito, TipoDelito.id_tipo_delito == Delito.id_tipo_delito)\
         .filter(filtro_fecha)\
         .group_by(TipoDelito.nombre_tipo_delito).all()
        
        distribution = [{"type": row.nombre_tipo_delito, "count": row.total} for row in crimes_by_type]

        # 3. Tendencia (Agrupado por día o mes dependiendo del filtro)
        # Si filtramos por año entero, mostramos tendencia por mes en vez de día para que sea legible
        if anio:
            trend_query = self.db.query(
                func.extract('month', Delito.fecha_delito).label('mes'),
                func.count(Delito.id_delito).label('total')
            ).filter(filtro_fecha)\
             .group_by(func.extract('month', Delito.fecha_delito))\
             .order_by(func.extract('month', Delito.fecha_delito)).all()
             
            trend = [{"date": f"{anio}-{int(row.mes):02d}-01", "count": row.total} for row in trend_query]
        else:
            seven_days_ago = datetime.now() - timedelta(days=7)
            weekly_trend = self.db.query(
                Delito.fecha_delito,
                func.count(Delito.id_delito).label('total')
            ).filter(Delito.fecha_delito >= seven_days_ago)\
             .group_by(Delito.fecha_delito)\
             .order_by(Delito.fecha_delito).all()
             
            trend = [{"date": str(row.fecha_delito), "count": row.total} for row in weekly_trend]

        # 4. Zonas Críticas (Top 5 Cuadrantes)
        top_zones = self.db.query(
            Cuadrante.nombre_cuadrante,
            func.count(Delito.id_delito).label('total')
        ).join(Delito, Cuadrante.id_cuadrante == Delito.id_cuadrante)\
         .filter(filtro_fecha)\
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

    def get_mapa_geojson(self):
        """
        Extrae los delitos recientes y los convierte en coordenadas Lat/Lng.
        Utiliza func.ST_X y func.ST_Y para extraer la geometría nativa de PostGIS.
        """
        # Obtenemos los últimos 5000 delitos (para no sobrecargar el navegador de golpe)
        delitos = self.db.query(
            Delito.id_delito,
            func.ST_Y(Delito.ubicacion_exacta).label('lat'),
            func.ST_X(Delito.ubicacion_exacta).label('lng'),
            TipoDelito.nombre_tipo_delito.label('tipo'),
        ).join(TipoDelito, Delito.id_tipo_delito == TipoDelito.id_tipo_delito)\
         .order_by(Delito.fecha_delito.desc())\
         .limit(5000).all()

        puntos = []
        for d in delitos:
            puntos.append({
                "id": d.id_delito,
                "lat": float(d.lat) if d.lat else 0,
                "lng": float(d.lng) if d.lng else 0,
                "tipo": d.tipo
            })
            
        return puntos

    def get_analisis(self, anio: int = None):
        if anio:
            filtro_fecha = func.extract('year', Delito.fecha_delito) == anio
        else:
            thirty_days_ago = datetime.now() - timedelta(days=30)
            filtro_fecha = Delito.fecha_delito >= thirty_days_ago

        # 1. KPIs
        total_delitos = self.db.query(func.count(Delito.id_delito)).filter(filtro_fecha).scalar() or 0
        
        distinct_days = self.db.query(func.count(func.distinct(Delito.fecha_delito))).filter(filtro_fecha).scalar() or 1
        promedio_diario = round(total_delitos / distinct_days, 1)

        # Pico Horario
        pico_query = self.db.query(
            func.extract('hour', Delito.hora_delito).label('hora'),
            func.count(Delito.id_delito).label('total')
        ).filter(filtro_fecha).group_by(func.extract('hour', Delito.hora_delito))\
         .order_by(text('total DESC')).first()
        
        pico_horario = f"{int(pico_query.hora):02d}:00" if pico_query and pico_query.hora is not None else "18:00"
        pico_count = pico_query.total if pico_query else 0

        # Zona más afectada (Distrito con más incidentes)
        zona_query = self.db.query(
            Distrito.nombre_distrito,
            func.count(Delito.id_delito).label('total')
        ).join(Cuadrante, Cuadrante.id_distrito == Distrito.id_distrito)\
         .join(Delito, Delito.id_cuadrante == Cuadrante.id_cuadrante)\
         .filter(filtro_fecha).group_by(Distrito.nombre_distrito)\
         .order_by(text('total DESC')).first()
        
        zona_mas_afectada = zona_query.nombre_distrito if zona_query else "Ninguno"
        zona_count = zona_query.total if zona_query else 0

        kpis = [
            {"label": "Total Delitos", "value": f"{total_delitos:,}", "change": "Datos reales del sistema"},
            {"label": "Promedio Diario", "value": f"{promedio_diario}", "change": "Incidentes por día"},
            {"label": "Pico Horario", "value": pico_horario, "change": f"{pico_count} delitos en esa hora"},
            {"label": "Distrito Más Afectado", "value": zona_mas_afectada, "change": f"{zona_count} incidentes"},
        ]

        # 2. Tendencia Mensual por Tipo de Delito
        # Necesitamos agrupar por mes y clasificar tipo de delito
        meses_nombres = {1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun', 
                         7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'}
        
        monthly_query = self.db.query(
            func.extract('month', Delito.fecha_delito).label('mes'),
            TipoDelito.nombre_tipo_delito,
            func.count(Delito.id_delito).label('total')
        ).join(TipoDelito, Delito.id_tipo_delito == TipoDelito.id_tipo_delito)\
         .filter(filtro_fecha)\
         .group_by(func.extract('month', Delito.fecha_delito), TipoDelito.nombre_tipo_delito).all()
        
        # Mapeamos a la estructura de Recharts
        # { month: 'Ene', robo: X, asalto: Y, vandalismo: Z, fraude: W }
        monthly_map = {}
        for row in monthly_query:
            m_num = int(row.mes)
            m_name = meses_nombres.get(m_num, str(m_num))
            if m_name not in monthly_map:
                monthly_map[m_name] = {"month": m_name, "robo": 0, "asalto": 0, "vandalismo": 0, "fraude": 0}
            
            # Clasificación
            name_upper = row.nombre_tipo_delito.upper()
            if "ROBO" in name_upper:
                monthly_map[m_name]["robo"] += row.total
            elif "HURTO" in name_upper or "ASALTO" in name_upper:
                monthly_map[m_name]["asalto"] += row.total
            elif "VANDALISMO" in name_upper:
                monthly_map[m_name]["vandalismo"] += row.total
            else:
                monthly_map[m_name]["fraude"] += row.total

        # Ordenar por meses del año
        sorted_months = sorted(monthly_map.keys(), key=lambda x: list(meses_nombres.values()).index(x) if x in meses_nombres.values() else 99)
        monthly_by_type = [monthly_map[m] for m in sorted_months]
        if not monthly_by_type:
            monthly_by_type = [{"month": m_lbl, "robo": 0, "asalto": 0, "vandalismo": 0, "fraude": 0} for m_val, m_lbl in list(meses_nombres.items())[:6]]

        # 3. Patrón Horario
        hourly_query = self.db.query(
            func.extract('hour', Delito.hora_delito).label('hora'),
            func.count(Delito.id_delito).label('total')
        ).filter(filtro_fecha).group_by(func.extract('hour', Delito.hora_delito))\
         .order_by(func.extract('hour', Delito.hora_delito)).all()

        hourly_pattern = []
        for row in hourly_query:
            if row.hora is not None:
                hourly_pattern.append({"hour": str(int(row.hora)), "v": row.total})
        if not hourly_pattern:
            hourly_pattern = [{"hour": "12", "v": 0}]

        # 4. Patrón Semanal
        # ISODOW va de 1 (Lunes) a 7 (Domingo)
        days_names = {1: 'Lun', 2: 'Mar', 3: 'Mié', 4: 'Jue', 5: 'Vie', 6: 'Sáb', 7: 'Dom'}
        weekly_query = self.db.query(
            func.extract('isodow', Delito.fecha_delito).label('dia'),
            func.count(Delito.id_delito).label('total')
        ).filter(filtro_fecha).group_by(func.extract('isodow', Delito.fecha_delito))\
         .order_by(func.extract('isodow', Delito.fecha_delito)).all()

        weekly_pattern = []
        for row in weekly_query:
            if row.dia is not None:
                weekly_pattern.append({"day": days_names.get(int(row.dia), str(row.dia)), "v": row.total})
        # Ordenar de Lun a Dom
        weekly_pattern.sort(key=lambda x: list(days_names.values()).index(x["day"]) if x["day"] in days_names.values() else 99)
        if not weekly_pattern:
            weekly_pattern = [{"day": "Lun", "v": 0}]

        # 5. Distribución de delitos
        dist_query = self.db.query(
            TipoDelito.nombre_tipo_delito,
            func.count(Delito.id_delito).label('total')
        ).join(TipoDelito, Delito.id_tipo_delito == TipoDelito.id_tipo_delito)\
         .filter(filtro_fecha).group_by(TipoDelito.nombre_tipo_delito).all()
        
        # Mapeamos a las 4 categorías
        dist_map = {"Robo": 0, "Asalto": 0, "Vandalismo": 0, "Fraude": 0}
        colors = {"Robo": "#ef4444", "Asalto": "#f97316", "Vandalismo": "#eab308", "Fraude": "#3b82f6"}
        for row in dist_query:
            name_upper = row.nombre_tipo_delito.upper()
            if "ROBO" in name_upper:
                dist_map["Robo"] += row.total
            elif "HURTO" in name_upper or "ASALTO" in name_upper:
                dist_map["Asalto"] += row.total
            elif "VANDALISMO" in name_upper:
                dist_map["Vandalismo"] += row.total
            else:
                dist_map["Fraude"] += row.total

        crime_distribution = [{"name": k, "value": v, "color": colors[k]} for k, v in dist_map.items()]

        # 6. Comparación de Zonas (Últimos 6 meses)
        # Obtenemos los top 5 distritos con más delitos
        top5_distritos = self.db.query(
            Distrito.id_distrito,
            Distrito.nombre_distrito,
            func.count(Delito.id_delito).label('total')
        ).join(Cuadrante, Cuadrante.id_distrito == Distrito.id_distrito)\
         .join(Delito, Delito.id_cuadrante == Cuadrante.id_cuadrante)\
         .filter(filtro_fecha).group_by(Distrito.id_distrito, Distrito.nombre_distrito)\
         .order_by(text('total DESC')).limit(5).all()

        zone_table = []
        # Para cada uno de estos distritos, obtenemos sus delitos de los últimos 6 meses
        months_to_show = [(1, "Ene"), (2, "Feb"), (3, "Mar"), (4, "Abr"), (5, "May"), (6, "Jun")]

        for dist in top5_distritos:
            row_data = {"zone": dist.nombre_distrito}
            for m_val, m_lbl in months_to_show:
                cnt = self.db.query(func.count(Delito.id_delito))\
                    .join(Cuadrante, Cuadrante.id_cuadrante == Delito.id_cuadrante)\
                    .filter(Cuadrante.id_distrito == dist.id_distrito)\
                    .filter(func.extract('month', Delito.fecha_delito) == m_val)\
                    .scalar() or 0
                row_data[m_lbl.lower()] = cnt
            zone_table.append(row_data)

        if not zone_table:
            any_d = self.db.query(Distrito.nombre_distrito).limit(5).all()
            zone_table = [{"zone": d.nombre_distrito, "ene": 0, "feb": 0, "mar": 0, "abr": 0, "may": 0, "jun": 0} for d in any_d]

        return {
            "kpis": kpis,
            "monthly_by_type": monthly_by_type,
            "hourly_pattern": hourly_pattern,
            "weekly_pattern": weekly_pattern,
            "crime_distribution": crime_distribution,
            "zone_table": zone_table
        }

    def get_stats_distrito(self, distrito_nombre: str):
        query = self.db.query(
            TipoDelito.nombre_tipo_delito,
            func.count(Delito.id_delito).label('total')
        ).join(Delito, Delito.id_tipo_delito == TipoDelito.id_tipo_delito)\
         .join(Cuadrante, Cuadrante.id_cuadrante == Delito.id_cuadrante)\
         .join(Distrito, Distrito.id_distrito == Cuadrante.id_distrito)
         
        if distrito_nombre.upper() != "TODOS":
            query = query.filter(func.upper(Distrito.nombre_distrito) == distrito_nombre.upper())
            
        results = query.group_by(TipoDelito.nombre_tipo_delito).all()

        stats = []
        total_crimes = sum(row.total for row in results) or 1
        for row in results:
            # Calcular porcentaje para la barra de progreso
            percentage = round((row.total / total_crimes) * 100, 1)
            stats.append({
                "name": row.nombre_tipo_delito,
                "value": percentage
            })

        if not stats:
            tipos = self.db.query(TipoDelito.nombre_tipo_delito).all()
            stats = [{"name": t.nombre_tipo_delito, "value": 0.0} for t in tipos]
        return stats
