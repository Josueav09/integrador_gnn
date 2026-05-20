import time
from fastapi import Request, HTTPException, status
from src.utils.logger import logger

# Diccionario en memoria para rastrear IPs: { "172.20.0.1": {"intentos": 2, "bloqueado_hasta": 0} }
# Nota de Arquitectura: En un sistema multi-servidor esto usaría Redis, 
# pero para un Monolito, la memoria RAM es el enfoque más veloz.
registro_ips = {}

MAX_INTENTOS = 5
TIEMPO_BLOQUEO_MINUTOS = 15

def verificar_bloqueo_ip(request: Request) -> str:
    """Verifica si la IP actual tiene permitido intentar loguearse."""
    ip = request.client.host
    tiempo_actual = time.time()

    # Si es la primera vez que vemos esta IP, la registramos
    if ip not in registro_ips:
        registro_ips[ip] = {"intentos": 0, "bloqueado_hasta": 0}

    # Si la IP está en periodo de castigo
    if registro_ips[ip]["bloqueado_hasta"] > tiempo_actual:
        tiempo_restante = int((registro_ips[ip]["bloqueado_hasta"] - tiempo_actual) / 60) + 1
        logger.warning(f"Ataque mitigado: IP {ip} bloqueada por {tiempo_restante} minutos más.")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Demasiados intentos fallidos. Su IP ha sido bloqueada por seguridad. Intente en {tiempo_restante} minutos."
        )

    return ip

def registrar_falla(ip: str):
    """Aumenta el contador de fallas. Si llega al límite, bloquea la IP."""
    registro_ips[ip]["intentos"] += 1
    
    if registro_ips[ip]["intentos"] >= MAX_INTENTOS:
        # Castigamos la IP agregando 15 minutos al tiempo actual
        registro_ips[ip]["bloqueado_hasta"] = time.time() + (TIEMPO_BLOQUEO_MINUTOS * 60)
        registro_ips[ip]["intentos"] = 0 # Reiniciamos el contador para su próximo intento válido
        logger.critical(f"DEFENSA ACTIVA: IP {ip} bloqueada por fuerza bruta (Máx. {MAX_INTENTOS} intentos).")

def resetear_intentos(ip: str):
    """Si el usuario hace un login exitoso, limpiamos su historial de fallas."""
    if ip in registro_ips:
        registro_ips[ip]["intentos"] = 0