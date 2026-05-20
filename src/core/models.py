from sqlalchemy import Column, Integer, String, ForeignKey
from src.core.database import Base

class Usuario(Base):
    __tablename__ = "sistema_usuarios"

    id_usuario_sistema = Column(Integer, primary_key=True, index=True)
    id_rol = Column(Integer, nullable=False)
    nombre_usuario_sistema = Column(String(100), nullable=False)
    apellido_usuario_sistema = Column(String(100), nullable=False)
    email_usuario_sistema = Column(String(150), unique=True, index=True, nullable=False)
    password_usuario_sistema = Column(String(255), nullable=False)
    estado_usuario_sistema = Column(String(20), default="activo")