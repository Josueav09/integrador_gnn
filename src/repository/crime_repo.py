from sqlalchemy.orm import Session
from src.core.models import Delito
from src.repository.base import BaseRepository

class CrimeRepository(BaseRepository[Delito]):
    """
    Repositorio específico para la tabla 'delitos'.
    Maneja las consultas geoespaciales y temporales mediante el ORM.
    """
    def __init__(self, db: Session):
        super().__init__(Delito, db)

    def get_delitos_por_fecha(self, fecha_inicio: str, fecha_fin: str):
        """
        Obtener delitos en un rango de fechas.
        Retorna los objetos Delito mapeados por SQLAlchemy.
        """
        return self.db.query(self.model).filter(
            self.model.fecha_delito >= fecha_inicio,
            self.model.fecha_delito <= fecha_fin
        ).all()