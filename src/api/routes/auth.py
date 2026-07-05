from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel

from src.core.database import get_db
from src.repository.user_repo import UserRepository
from src.security.hashing import Hash
from src.security.jwt_handler import create_access_token
from src.utils.logger import logger
from src.services import email_service
import random
from fastapi import BackgroundTasks
from src.core.config import settings

# Importamos nuestro nuevo escudo
from src.security.rate_limit import (
    verificar_bloqueo_ip,
    registrar_falla,
    registrar_intento,
    resetear_intentos,
    ALCANCE_LOGIN,
    ALCANCE_FORGOT,
    ALCANCE_VERIFY_PIN,
)

router = APIRouter(prefix="/auth", tags=["Autenticación"])

from datetime import datetime, timedelta
from src.core.models import CodigoRecuperacion, Usuario

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    rol_id: int

class RegisterRequest(BaseModel):
    nombre: str
    apellido: str
    email: str
    password: str

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(credenciales: RegisterRequest, db: Session = Depends(get_db)):
    if len(credenciales.password) < 6:
        raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 6 caracteres.")

    user_repo = UserRepository(db)
    if user_repo.get_by_email(credenciales.email.strip()):
        raise HTTPException(status_code=400, detail="El correo ya está registrado.")

    nuevo_usuario = Usuario(
        id_rol=2,
        nombre_usuario_sistema=credenciales.nombre.strip(),
        apellido_usuario_sistema=credenciales.apellido.strip(),
        email_usuario_sistema=credenciales.email.strip().lower(),
        password_usuario_sistema=Hash.bcrypt(credenciales.password),
    )
    db.add(nuevo_usuario)
    db.commit()
    logger.info(f"Nuevo usuario registrado: {credenciales.email}")
    return {"success": True, "message": "Cuenta creada exitosamente."}

# FÍJATE AQUÍ: Agregamos "request: Request" y ejecutamos la verificación de IP
@router.post("/login", response_model=TokenResponse)
def login(request: Request, credenciales: LoginRequest, db: Session = Depends(get_db)):
    
    # 1. VERIFICACIÓN DE RATE LIMITING (Defensa Perimetral)
    ip_cliente = verificar_bloqueo_ip(request, ALCANCE_LOGIN)
    
    logger.info(f"Intento de acceso detectado para el usuario: {credenciales.email} desde IP: {ip_cliente}")
    
    user_repo = UserRepository(db)
    usuario = user_repo.get_by_email(credenciales.email)
    
    # Manejo genérico de errores + Registro de Falla
    if not usuario:
        logger.warning(f"Intento fallido: El correo {credenciales.email} no existe.")
        registrar_falla(ip_cliente, ALCANCE_LOGIN)
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
        registrar_falla(ip_cliente, ALCANCE_LOGIN)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Credenciales incorrectas"
        )
        
    # Si llegó hasta aquí, el login fue exitoso. Limpiamos su historial.
    resetear_intentos(ip_cliente, ALCANCE_LOGIN)
    logger.info(f"Acceso exitoso. Generando Token JWT para {credenciales.email}.")
    
    rol_str = str(usuario.id_rol)
    access_token = create_access_token(user_id=usuario.id_usuario_sistema, rol=rol_str)
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "rol_id": usuario.id_rol
    }

class ForgotPasswordRequest(BaseModel):
    email: str

class VerifyCodeRequest(BaseModel):
    email: str
    code: str

class ResetPasswordRequest(BaseModel):
    email: str
    code: str
    newPassword: str

@router.post("/forgot-password")
def forgot_password(
    http_request: Request,
    request: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    ip_cliente = verificar_bloqueo_ip(http_request, ALCANCE_FORGOT)
    registrar_intento(ip_cliente, ALCANCE_FORGOT)
    user_repo = UserRepository(db)
    usuario = user_repo.get_by_email(request.email)
    
    if usuario and usuario.estado_usuario_sistema == "activo":
        pin = settings.TEST_PIN if settings.TEST_MODE else str(random.randint(100000, 999999))
        if settings.TEST_MODE:
            logger.info(f"[TEST_MODE] PIN de recuperación para {request.email}: {pin}")
        
        # 2. Calcular expiración (15 minutos desde ahora)
        expiracion = datetime.utcnow() + timedelta(minutes=15)
        
        # 3. Guardar en Base de Datos (Persistencia)
        nuevo_codigo = CodigoRecuperacion(
            email_usuario=request.email, 
            pin_recuperacion=pin, 
            fecha_expiracion=expiracion
        )
        db.add(nuevo_codigo)
        db.commit()
        
        # 4. Enviar de forma asíncrona
        background_tasks.add_task(email_service.enviar_pin_recuperacion, request.email, pin)
    else:
        logger.warning(f"Intento de recuperación inválido para: {request.email}")
        # En caso de recuperación fraudulenta o spam a correos inexistentes,
        # penalizamos a la IP atacante para evitar escaneo o saturación SMTP.
        registrar_falla(ip_cliente, ALCANCE_FORGOT)
        
    # Siempre retornamos éxito para prevenir enumeración de usuarios (OWASP)
    return {"success": True, "message": "Si el correo existe y está activo, se le enviará un código de recuperación."}

@router.post("/verify-code")
def verify_code(http_request: Request, request: VerifyCodeRequest, db: Session = Depends(get_db)):
    ip_cliente = verificar_bloqueo_ip(http_request, ALCANCE_VERIFY_PIN)
    # Buscar el PIN no usado y que no haya expirado
    codigo_db = db.query(CodigoRecuperacion).filter(
        CodigoRecuperacion.email_usuario == request.email,
        CodigoRecuperacion.pin_recuperacion == request.code,
        CodigoRecuperacion.usado == False
    ).first()
    
    if not codigo_db:
        registrar_falla(ip_cliente, ALCANCE_VERIFY_PIN)
        raise HTTPException(status_code=400, detail="El código es incorrecto.")
        
    # IMPORTANTE: Validar tiempo (Time-Based Security)
    if codigo_db.fecha_expiracion.replace(tzinfo=None) < datetime.utcnow():
        registrar_falla(ip_cliente, ALCANCE_VERIFY_PIN)
        raise HTTPException(status_code=400, detail="El código ha expirado.")
        
    resetear_intentos(ip_cliente, ALCANCE_VERIFY_PIN)
    return {"success": True, "message": "Código verificado correctamente."}

@router.post("/reset-password")
def reset_password(http_request: Request, request: ResetPasswordRequest, db: Session = Depends(get_db)):
    # 1. VERIFICACIÓN DE RATE LIMITING
    ip_cliente = verificar_bloqueo_ip(http_request)
    
    codigo_db = db.query(CodigoRecuperacion).filter(
        CodigoRecuperacion.email_usuario == request.email,
        CodigoRecuperacion.pin_recuperacion == request.code,
        CodigoRecuperacion.usado == False
    ).first()
    
    if not codigo_db or codigo_db.fecha_expiracion.replace(tzinfo=None) < datetime.utcnow():
        registrar_falla(ip_cliente)
        raise HTTPException(status_code=400, detail="El código es incorrecto o ha expirado.")
        
    user_repo = UserRepository(db)
    usuario = user_repo.get_by_email(request.email)
    
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
        
    # 1. Actualizar Hash de Contraseña
    usuario.password_usuario_sistema = Hash.bcrypt(request.newPassword)
    
    # 2. Quemar el código para que no pueda reutilizarse (Mitigación de Replay Attacks)
    codigo_db.usado = True
    
    db.commit()
    
    # Resetear penalizaciones tras un restablecimiento exitoso
    resetear_intentos(ip_cliente)
    
    logger.info(f"El usuario {request.email} ha restablecido su contraseña con éxito.")
    return {"success": True, "message": "Contraseña restablecida exitosamente."}