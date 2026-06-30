from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, validator, field_validator
from datetime import date, time
import re

from src.core.database import get_db
from src.repository.denuncia_repo import DenunciaRepository
from src.security.jwt_handler import get_current_user
from src.security.rate_limit import verificar_bloqueo_ip, registrar_falla, ALCANCE_DENUNCIA

router = APIRouter(prefix="/denuncias", tags=["Denuncias Ciudadanas (Cuarentena)"])

class DenunciaCreate(BaseModel):
    id_tipo_delito: int
    fecha_delito: date
    hora_delito: time
    latitud: float
    longitud: float
    descripcion: str

    @field_validator('descripcion')
    @classmethod
    def validar_xss_sqli(cls, v: str) -> str:
        # Prevención básica de XSS y SQLi (OWASP)
        # Rechaza scripts, iframes o intentos de inyección
        patrones_peligrosos = [
            r"<script.*?>.*?</script.*?>",
            r"<.*?javascript:.*?>",
            r"<.*?onload=.*?>",
            r"<.*?onerror=.*?>",
            r"DROP TABLE",
            r"DELETE FROM",
            r"UNION SELECT"
        ]
        for patron in patrones_peligrosos:
            if re.search(patron, v, re.IGNORECASE):
                raise ValueError("Contenido bloqueado por política de seguridad (Posible ataque XSS/SQLi).")
        return v

@router.post("/publica", status_code=status.HTTP_201_CREATED)
def registrar_denuncia_publica(request: Request, denuncia: DenunciaCreate, db: Session = Depends(get_db)):
    """
    Ruta pública (sin JWT) para registro de incidencias por parte de ciudadanos.
    Utiliza el Rate Limiting estricto para evitar DDoS de datos falsos.
    """
    try:
        ip_cliente = verificar_bloqueo_ip(request, ALCANCE_DENUNCIA)
    except HTTPException as e:
        raise e

    try:
        repo = DenunciaRepository(db)
        nueva_denuncia = repo.create_denuncia_publica(
            id_tipo_delito=denuncia.id_tipo_delito,
            fecha_delito=denuncia.fecha_delito,
            hora_delito=denuncia.hora_delito,
            lat=denuncia.latitud,
            lng=denuncia.longitud,
            descripcion=denuncia.descripcion
        )
        return {"success": True, "message": "Denuncia recibida en cola de verificación.", "id": nueva_denuncia.id_denuncia_ciudadana}
    except ValueError as ve:
        # Registramos la falla contra la IP por intento malicioso
        registrar_falla(ip_cliente, ALCANCE_DENUNCIA)
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        registrar_falla(ip_cliente, ALCANCE_DENUNCIA)
        raise HTTPException(status_code=500, detail="Error interno al registrar denuncia")

@router.get("/pendientes")
def obtener_denuncias_pendientes(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """
    Ruta protegida para que los analistas PNP vean la bandeja de entrada de denuncias.
    """
    repo = DenunciaRepository(db)
    pendientes = repo.get_denuncias_pendientes()
    return {"success": True, "data": pendientes}

@router.post("/aprobar/{id_denuncia}")
def aprobar_denuncia(id_denuncia: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """
    Aprueba una denuncia, calculando su cuadrante mediante PostGIS y moviéndola a la tabla oficial de delitos.
    """
    repo = DenunciaRepository(db)
    try:
        denuncia_aprobada = repo.aprobar_denuncia(id_denuncia)
        if not denuncia_aprobada:
            raise HTTPException(status_code=404, detail="Denuncia no encontrada o ya procesada.")
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    
    # Registro de auditoría (quién aprobó la denuncia)
    # logger.info(f"Analista ID {current_user['user_id']} aprobó la denuncia ciudadana {id_denuncia}")
    
    return {"success": True, "message": "Denuncia aprobada y transferida al registro histórico."}

@router.post("/rechazar/{id_denuncia}")
def rechazar_denuncia(id_denuncia: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    """
    Rechaza una denuncia ciudadana.
    """
    repo = DenunciaRepository(db)
    denuncia_rechazada = repo.rechazar_denuncia(id_denuncia)
    if not denuncia_rechazada:
        raise HTTPException(status_code=404, detail="Denuncia no encontrada o ya procesada.")
    return {"success": True, "message": "Denuncia rechazada exitosamente."}
