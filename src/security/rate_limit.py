import time
from fastapi import Request, HTTPException, status
from src.utils.logger import logger

# Clave compuesta alcance:IP — evita que login bloquee denuncias públicas o viceversa.
registro_ips: dict[str, dict[str, float | int]] = {}

MAX_INTENTOS = 5
TIEMPO_BLOQUEO_MINUTOS = 15

ALCANCE_LOGIN = "login"
ALCANCE_DENUNCIA = "denuncia_publica"
ALCANCE_FORGOT = "forgot_password"
ALCANCE_VERIFY_PIN = "verify_code"


def _clave(ip: str, alcance: str) -> str:
    return f"{alcance}:{ip}"


def verificar_bloqueo_ip(request: Request, alcance: str = ALCANCE_LOGIN) -> str:
    """Verifica si la IP actual tiene permitido intentar la acción indicada."""
    ip = request.client.host if request.client else "unknown"
    tiempo_actual = time.time()
    clave = _clave(ip, alcance)

    if clave not in registro_ips:
        registro_ips[clave] = {"intentos": 0, "bloqueado_hasta": 0}

    if registro_ips[clave]["bloqueado_hasta"] > tiempo_actual:
        tiempo_restante = int((registro_ips[clave]["bloqueado_hasta"] - tiempo_actual) / 60) + 1
        logger.warning(
            f"Ataque mitigado [{alcance}]: IP {ip} bloqueada por {tiempo_restante} minutos más."
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Demasiados intentos fallidos. Su IP ha sido bloqueada por seguridad. Intente en {tiempo_restante} minutos.",
        )

    return ip


def registrar_falla(ip: str, alcance: str = ALCANCE_LOGIN) -> None:
    """Aumenta el contador de fallas. Si llega al límite, bloquea la IP para ese alcance."""
    clave = _clave(ip, alcance)
    if clave not in registro_ips:
        registro_ips[clave] = {"intentos": 0, "bloqueado_hasta": 0}

    registro_ips[clave]["intentos"] += 1

    if registro_ips[clave]["intentos"] >= MAX_INTENTOS:
        registro_ips[clave]["bloqueado_hasta"] = time.time() + (TIEMPO_BLOQUEO_MINUTOS * 60)
        registro_ips[clave]["intentos"] = 0
        logger.critical(
            f"DEFENSA ACTIVA [{alcance}]: IP {ip} bloqueada por fuerza bruta (Máx. {MAX_INTENTOS} intentos)."
        )


def resetear_intentos(ip: str, alcance: str = ALCANCE_LOGIN) -> None:
    """Limpia el historial de fallas tras una acción exitosa."""
    clave = _clave(ip, alcance)
    if clave in registro_ips:
        registro_ips[clave]["intentos"] = 0
        registro_ips[clave]["bloqueado_hasta"] = 0
