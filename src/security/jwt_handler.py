import time
import jwt
from typing import Dict
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# [ESTRATEGIA DE SEGURIDAD - ÍTEM 5 Y 6]
# Importamos las variables centralizadas
from src.core.config import settings

# Esto es lo que activa el botón "Authorize" en Swagger
security = HTTPBearer()

def create_access_token(user_id: int, rol: str) -> str:
    payload = {
        "user_id": user_id,
        "rol": rol,
        "expires": time.time() + (settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def verify_access_token(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if decoded_token["expires"] >= time.time():
            return decoded_token
        else:
            return {"error": "El token ha expirado. Inicie sesión nuevamente."}
    except jwt.ExpiredSignatureError:
        return {"error": "El token ha expirado."}
    except jwt.InvalidTokenError:
        return {"error": "Token inválido o manipulado."}

# NUEVA FUNCIÓN: Intercepta la petición, extrae el token del Header y lo valida
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = credentials.credentials
    payload = verify_access_token(token)
    
    if "error" in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=payload["error"],
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload

def get_current_admin_or_investigator(payload: dict = Depends(get_current_user)) -> dict:
    rol = payload.get("rol", "").lower()
    if rol not in ["administrador", "investigador", "1", "3"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operación no permitida para su rol. Requiere Administrador o Investigador."
        )
    return payload