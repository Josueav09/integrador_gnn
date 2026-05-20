from sqlalchemy.orm import Session
from src.core.models import Usuario
from src.repository.base import BaseRepository

class UserRepository(BaseRepository[Usuario]):
    """
    Repositorio específico para la tabla 'sistema_usuarios'.
    Hereda el CRUD básico (get_by_id, create, etc.) de BaseRepository
    y añade métodos específicos del negocio.
    """
    def __init__(self, db: Session):
        super().__init__(Usuario, db)

    def get_by_email(self, email: str) -> Usuario | None:
        """Busca un usuario policial específicamente por su correo electrónico."""
        return self.db.query(self.model).filter(self.model.email_usuario_sistema == email).first()