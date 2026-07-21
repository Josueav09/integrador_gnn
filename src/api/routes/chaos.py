from fastapi import APIRouter, HTTPException, status

from src.core.config import settings
from src.utils.logger import logger

router = APIRouter(prefix="/admin/chaos", tags=["Mantenimiento y Resiliencia"])


@router.post("/crash")
def simulate_container_crash():
    """
    Simulación controlada de un fallo severo para pruebas de mantenimiento.

    La ejecución real destructiva queda deshabilitada para evitar detener
    el proceso del servidor durante pruebas automatizadas o en producción.
    """
    if not settings.TEST_MODE:
        logger.warning("[CHAOS] Intento bloqueado fuera de TEST_MODE.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Endpoint disponible solo en modo laboratorio.",
        )

    logger.critical("[CHAOS] Simulación controlada de caída activada en TEST_MODE.")
    return {
        "status": "simulado",
        "message": "Se ejecutó una simulación controlada de falla sin detener el proceso.",
        "modo": "TEST_MODE",
    }