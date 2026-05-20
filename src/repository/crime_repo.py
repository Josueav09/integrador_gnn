from sqlalchemy.orm import Session
from src.repository.base import BaseRepository
from sqlalchemy import text

class CrimeRepository(BaseRepository):
    """
    Repositorio específico para la tabla 'delitos'.
    Manejará las consultas geoespaciales (PostGIS) requeridas por el Frontend.
    """
    def __init__(self, db: Session, model):
        super().__init__(model, db)

    def get_delitos_por_fecha(self, fecha_inicio: str, fecha_fin: str):
        """
        Ejemplo de consulta futura para el Frontend: 
        Obtener delitos en un rango de fechas para pintar en el mapa de React.
        """
        query = text("""
            SELECT id_delito, tipo_delito, latitud, longitud, fecha_hora 
            FROM delitos 
            WHERE fecha_hora BETWEEN :inicio AND :fin
        """)
        return self.db.execute(query, {"inicio": fecha_inicio, "fin": fecha_fin}).fetchall()