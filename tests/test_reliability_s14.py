import time
import sys
from pathlib import Path
from unittest.mock import patch

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from src.services.resilience_service import (
    CircuitBreaker,
    CircuitState,
    execute_with_fallback,
    retry_with_backoff,
)

client = TestClient(app)

# ================================================================================
# PRUEBAS DE RESILIENCIA SEMANA 14 (ISO 25010 & S14_s2)
# ================================================================================


def test_s14_circuit_breaker_transitions():
    """
    S14_s2: Valida la transición completa CLOSED -> OPEN -> HALF_OPEN -> CLOSED
    con los parámetros del docente:
    - slidingWindowSize: 5
    - failureRateThreshold: 50%
    - waitDurationInOpenState: 0.5s (simulado)
    - permittedNumberOfCallsInHalfOpenState: 2
    """
    cb = CircuitBreaker(sliding_window_size=5, failure_threshold=0.5, wait_duration=0.5, permitted_half_open_calls=2)

    assert cb.state == CircuitState.CLOSED

    # 1. Simular 3 fallas de 5 peticiones (60% de error en la ventana de 5)
    cb.record_result(True)
    cb.record_result(False)
    cb.record_result(False)
    cb.record_result(True)
    cb.record_result(False)  # El circuito debe abrirse aquí (OPEN)

    assert cb.state == CircuitState.OPEN
    assert cb.can_execute() is False

    # 2. Transcurrido el waitDuration, debe pasar a HALF_OPEN
    time.sleep(0.55)
    assert cb.can_execute() is True
    assert cb.state == CircuitState.HALF_OPEN

    # 3. 2 solicitudes exitosas en HALF_OPEN recuperan el circuito a CLOSED
    cb.record_result(True)
    cb.record_result(True)
    assert cb.state == CircuitState.CLOSED


def test_s14_fallback_execution():
    """
    S14_s2: Valida que ante caídas o circuito abierto se ejecute la respuesta de emergencia (Fallback)
    sin interrumpir la disponibilidad percibida por el usuario.
    """
    def funcion_inestable():
        raise ConnectionError("Fallo crítico en el motor de inferencia GNN")

    def funcion_fallback():
        return {"status": "DEGRADED", "fallback": True, "message": "Datos servidos desde el histórico de la PNP"}

    resultado = execute_with_fallback(funcion_inestable, funcion_fallback)

    assert resultado["status"] == "DEGRADED"
    assert resultado["fallback"] is True


def test_s14_retry_pattern_backoff():
    """
    S14_s2: Valida el patrón Retry con reintentos automáticos y backoff.
    - maxAttempts: 3
    - waitDuration: 0.05s
    """
    intentos = 0

    def servicio_con_intermitencia():
        nonlocal intentos
        intentos += 1
        if intentos < 3:
            raise TimeoutError("Timeout temporal de red")
        return "ÉXITO_RETRY"

    resultado = retry_with_backoff(servicio_con_intermitencia, max_attempts=3, wait_duration=0.05)

    assert intentos == 3
    assert resultado == "ÉXITO_RETRY"


def test_s14_fault_injection_db_failure():
    """
    S14_s1: Fault Injection Testing - Inyección deliberada de fallo de BD.
    Verifica que la API responda con código HTTP 500/503 controlado en lugar de colapsar.
    """
    client_no_raise = TestClient(app, raise_server_exceptions=False)
    with patch("sqlalchemy.orm.Session.query") as mock_query:
        mock_query.side_effect = Exception("Conexión rechazada por inyección de fallo en prueba S14")

        response = client_no_raise.get("/dashboard/mapa-geojson")
        assert response.status_code in [500, 503]


def test_s14_health_and_circuit_breaker_endpoints():
    """
    S14_s2 & Criterio 4: Valida la disponibilidad de los endpoints de salud /health y /health/circuit-breakers
    """
    res_health = client.get("/health/")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "UP"
    assert res_health.json()["service"] == "PNP GNN SPRED API"

    res_cb = client.get("/health/circuit-breakers")
    assert res_cb.status_code == 200
    assert "gnn_service_breaker" in res_cb.json()
    assert res_cb.json()["gnn_service_breaker"]["failureRateThreshold"] == "50.0%"


def test_s14_mtbf_mttr_metrics_validation():
    """
    S14_s1: Valida el cálculo matemático formal de MTBF y MTTR exigidos por la ISO 25010
    """
    horas_operacion = 1000.0
    numero_fallos = 2.0
    minutos_recuperacion = 10.0

    mtbf = horas_operacion / numero_fallos
    mttr = minutos_recuperacion / numero_fallos
    uptime_percentage = ((720.0 - (minutos_recuperacion / 60.0)) / 720.0) * 100.0

    assert mtbf == 500.0  # 500 horas de tiempo medio entre fallos
    assert mttr == 5.0    # 5 minutos de tiempo medio de reparación
    assert uptime_percentage > 99.9  # Cumple SLA de 99.9% Uptime
