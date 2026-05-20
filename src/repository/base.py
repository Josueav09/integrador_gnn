from sqlalchemy.orm import Session
from typing import TypeVar, Generic, Type, Any

# Definimos un tipo genérico "T" que representará cualquier tabla (Delitos, Usuarios, etc.)
T = TypeVar("T")

class BaseRepository(Generic[T]):
    """
    Implementación del Patrón Repository (Data Access Object - DAO).
    Centraliza las operaciones CRUD para no repetir código en los controladores.
    """
    def __init__(self, model: Type[T], db: Session):
        self.model = model
        self.db = db

    def get_by_id(self, id: Any) -> T | None:
        """Busca un registro por su Llave Primaria."""
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> list[T]:
        """Obtiene una lista paginada de registros."""
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def create(self, obj_in: dict) -> T:
        """Inserta un nuevo registro en la base de datos."""
        obj_data = self.model(**obj_in)
        self.db.add(obj_data)
        self.db.commit()
        self.db.refresh(obj_data)
        return obj_data

    def delete(self, id: Any) -> bool:
        """Elimina un registro de manera segura."""
        obj = self.get_by_id(id)
        if obj:
            self.db.delete(obj)
            self.db.commit()
            return True
        return False