from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.core.database import get_db
from src.repository.user_repo import UserRepository
from src.security.hashing import Hash
from src.security.jwt_handler import create_access_token
from src.utils.logger import logger

# Importamos nuestro nuevo escudo
from src.security.rate_limit import verificar_bloqueo_ip, registrar_falla, resetear_intentos

router = APIRouter(prefix="/auth", tags=["Autenticación"])

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    rol_id: int

# FÍJATE AQUÍ: Agregamos "request: Request" y ejecutamos la verificación de IP
@router.post("/login", response_model=TokenResponse)
def login(request: Request, credenciales: LoginRequest, db: Session = Depends(get_db)):
    
    # 1. VERIFICACIÓN DE RATE LIMITING (Defensa Perimetral)
    ip_cliente = verificar_bloqueo_ip(request)
    
    logger.info(f"Intento de acceso detectado para el usuario: {credenciales.email} desde IP: {ip_cliente}")
    
    user_repo = UserRepository(db)
    usuario = user_repo.get_by_email(credenciales.email)
    
    # Manejo genérico de errores + Registro de Falla
    if not usuario:
        logger.warning(f"Intento fallido: El correo {credenciales.email} no existe.")
        registrar_falla(ip_cliente) # <--- Castigamos la IP
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Credenciales incorrectas"
        )
        
    if usuario.estado_usuario_sistema != "activo":
        logger.warning(f"Acceso denegado: Usuario {credenciales.email} inactivo.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="La cuenta policial se encuentra inactiva o suspendida"
        )
        
    if not Hash.verify(usuario.password_usuario_sistema, credenciales.password):
        logger.critical(f"ALERTA DE SEGURIDAD: Contraseña incorrecta para {credenciales.email}.")
        registrar_falla(ip_cliente) # <--- Castigamos la IP
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Credenciales incorrectas"
        )
        
    # Si llegó hasta aquí, el login fue exitoso. Limpiamos su historial.
    resetear_intentos(ip_cliente)
    logger.info(f"Acceso exitoso. Generando Token JWT para {credenciales.email}.")
    
    rol_str = str(usuario.id_rol)
    access_token = create_access_token(user_id=usuario.id_usuario_sistema, rol=rol_str)
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "rol_id": usuario.id_rol
    }