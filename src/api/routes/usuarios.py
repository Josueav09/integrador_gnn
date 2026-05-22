from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import List, Optional

from src.core.database import get_db
from src.core.models import Usuario, Rol
from src.repository.user_repo import UserRepository
from src.security.jwt_handler import get_current_user
from src.security.hashing import Hash
from src.services import email_service
from sqlalchemy import func

router = APIRouter(prefix="/usuarios", tags=["Gestión de Usuarios (CRUD)"])

# --- SCHEMAS ---
class UsuarioCreate(BaseModel):
    nombre: str
    email: EmailStr
    id_rol: int

class UsuarioResponse(BaseModel):
    id_usuario_sistema: int
    nombre_usuario_sistema: str
    email_usuario_sistema: str
    estado_usuario_sistema: str
    id_rol: int
    rol_nombre: str

    class Config:
        from_attributes = True

# --- MIDDLEWARE DE RBAC ---
def verificar_admin(current_user: dict = Depends(get_current_user)):
    """Verifica que el usuario actual tenga el rol 1 (Administrador)."""
    if str(current_user.get("rol")) != "1":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operación denegada. Solo los Administradores pueden gestionar usuarios."
        )
    return current_user

# --- RUTAS ---
@router.get("/", response_model=List[UsuarioResponse])
def listar_usuarios(db: Session = Depends(get_db), current_user: dict = Depends(verificar_admin)):
    """Lista todos los usuarios registrados junto con su rol."""
    usuarios = db.query(Usuario, Rol.nombre_rol).join(Rol, Usuario.id_rol == Rol.id_rol).all()
    resultado = []
    for user, rol_name in usuarios:
        resultado.append({
            "id_usuario_sistema": user.id_usuario_sistema,
            "nombre_usuario_sistema": user.nombre_usuario_sistema,
            "email_usuario_sistema": user.email_usuario_sistema,
            "estado_usuario_sistema": user.estado_usuario_sistema,
            "id_rol": user.id_rol,
            "rol_nombre": rol_name
        })
    return resultado

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def crear_usuario(
    usuario: UsuarioCreate, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db), 
    current_user: dict = Depends(verificar_admin)
):
    """Crea un nuevo usuario policial y despacha correo de bienvenida en Background."""
    repo = UserRepository(db)
    
    # Validar si el email ya existe
    if repo.get_by_email(usuario.email):
        raise HTTPException(status_code=400, detail="El correo electrónico ya está registrado.")
    
    # Generar contraseña temporal genérica (Ej: Cambiar123)
    # En producción se generaría un random string.
    temp_password = "Password123*"
    hashed_pwd = Hash.bcrypt(temp_password)
    
    partes = usuario.nombre.split(" ", 1)
    nombre_db = partes[0]
    apellido_db = partes[1] if len(partes) > 1 else ""
    
    nuevo_usuario = Usuario(
        nombre_usuario_sistema=nombre_db,
        apellido_usuario_sistema=apellido_db,
        email_usuario_sistema=usuario.email,
        password_usuario_sistema=hashed_pwd,
        estado_usuario_sistema="activo",
        id_rol=usuario.id_rol
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    
    # Despachar correo asíncrono (Fase 2) sin bloquear el hilo
    background_tasks.add_task(email_service.enviar_bienvenida, usuario.email, temp_password)
    
    return {"success": True, "message": "Usuario creado con éxito. Correo de bienvenida encolado."}

@router.delete("/{id_usuario}")
def desactivar_usuario(id_usuario: int, db: Session = Depends(get_db), current_user: dict = Depends(verificar_admin)):
    """No borramos usuarios por integridad referencial, solo los inactivamos."""
    usuario = db.query(Usuario).filter(Usuario.id_usuario_sistema == id_usuario).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
    usuario.estado_usuario_sistema = "inactivo"
    db.commit()
    return {"success": True, "message": f"Usuario {id_usuario} desactivado correctamente."}
