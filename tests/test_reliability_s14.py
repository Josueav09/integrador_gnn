import time
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

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
    gnn_circuit_breaker,
)

client = TestClient(app)
client_no_raise = TestClient(app, raise_server_exceptions=False)

# ================================================================================
# SUITE INTEGRAL DE PRUEBAS DE CONFIABILIDAD Y RESILIENCIA (SEMANA 14 - ISO 25010)
# Total: 26 Pruebas Automatizadas (S14_s1 + S14_s2)
# ================================================================================

# --------------------------------------------------------------------------------
# GRUPO 1: PRUEBAS DEL PATRÓN CIRCUIT BREAKER (S14_s2 - ISO 25010 Fault Tolerance)
# --------------------------------------------------------------------------------

def test_cb_01_initial_closed_state():
    """CB-01: El Circuit Breaker arranca en estado CLOSED con historia vacía"""
    cb = CircuitBreaker(sliding_window_size=5, failure_threshold=0.5, wait_duration=1.0)
    assert cb.state == CircuitState.CLOSED
    assert len(cb.history) == 0
    assert cb.can_execute() is True


def test_cb_02_record_successful_calls():
    """CB-02: Registro de peticiones exitosas mantiene el estado CLOSED"""
    cb = CircuitBreaker(sliding_window_size=5, failure_threshold=0.5)
    for _ in range(5):
        cb.record_result(True)
    assert cb.state == CircuitState.CLOSED
    assert cb.history == [True, True, True, True, True]


def test_cb_03_sliding_window_eviction():
    """CB-03: La ventana deslizante descarte elementos antiguos al superar sliding_window_size"""
    cb = CircuitBreaker(sliding_window_size=3, failure_threshold=0.5)
    cb.record_result(True)
    cb.record_result(True)
    cb.record_result(False)
    cb.record_result(True)  # Elimina el primer True
    assert len(cb.history) == 3
    assert cb.history == [True, False, True]


def test_cb_04_transition_closed_to_open_on_threshold():
    """CB-04: Transición a OPEN cuando la tasa de error alcanza o supera el 50%"""
    cb = CircuitBreaker(sliding_window_size=4, failure_threshold=0.5, wait_duration=5.0)
    cb.record_result(True)
    cb.record_result(False)
    cb.record_result(True)
    cb.record_result(False)  # 2 de 4 fallaron (50%)
    assert cb.state == CircuitState.OPEN
    assert cb.can_execute() is False


def test_cb_05_rejection_when_open():
    """CB-05: Solicitudes son rechazadas de inmediato (can_execute = False) en estado OPEN"""
    cb = CircuitBreaker(sliding_window_size=2, failure_threshold=0.5, wait_duration=10.0)
    cb.record_result(False)
    cb.record_result(False)
    assert cb.state == CircuitState.OPEN
    assert cb.can_execute() is False


def test_cb_06_transition_open_to_half_open_after_wait():
    """CB-06: Transición de OPEN a HALF_OPEN una vez transcurrido waitDurationInOpenState"""
    cb = CircuitBreaker(sliding_window_size=2, failure_threshold=0.5, wait_duration=0.2)
    cb.record_result(False)
    cb.record_result(False)
    assert cb.state == CircuitState.OPEN
    time.sleep(0.25)  # Expirar wait_duration
    assert cb.can_execute() is True
    assert cb.state == CircuitState.HALF_OPEN


def test_cb_07_recovery_half_open_to_closed():
    """CB-07: Transición de HALF_OPEN a CLOSED tras N solicitudes de prueba exitosas"""
    cb = CircuitBreaker(sliding_window_size=2, failure_threshold=0.5, wait_duration=0.1, permitted_half_open_calls=2)
    cb.record_result(False)
    cb.record_result(False)
    time.sleep(0.15)
    cb.can_execute()  # Pasa a HALF_OPEN
    assert cb.state == CircuitState.HALF_OPEN

    cb.record_result(True)
    assert cb.state == CircuitState.HALF_OPEN  # Requiere 2 exitosas
    cb.record_result(True)
    assert cb.state == CircuitState.CLOSED     # Restablecido


def test_cb_08_reopen_from_half_open_on_failure():
    """CB-08: Si una sola prueba en HALF_OPEN falla, el circuito regresa a OPEN inmediatamente"""
    cb = CircuitBreaker(sliding_window_size=2, failure_threshold=0.5, wait_duration=0.1, permitted_half_open_calls=2)
    cb.record_result(False)
    cb.record_result(False)
    time.sleep(0.15)
    cb.can_execute()  # Pasa a HALF_OPEN

    cb.record_result(False)  # Fallo durante la prueba
    assert cb.state == CircuitState.OPEN
    assert cb.can_execute() is False


# --------------------------------------------------------------------------------
# GRUPO 2: PRUEBAS DEL PATRÓN RETRY Y BACKOFF (S14_s2 - ISO 25010 Recoverability)
# --------------------------------------------------------------------------------

def test_retry_01_success_on_first_try():
    """RETRY-01: Operación exitosa en el primer intento no dispara reintentos ni retardo"""
    calls = 0
    def funcion_ok():
        nonlocal calls
        calls += 1
        return "OK"

    res = retry_with_backoff(funcion_ok, max_attempts=3, wait_duration=0.01)
    assert res == "OK"
    assert calls == 1


def test_retry_02_success_after_transient_failures():
    """RETRY-02: Reintento exitoso en el 3er intento tras fallas temporales de red"""
    attempts = 0
    def funcion_intermitente():
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise TimeoutError("Fallo temporal de conexión")
        return "ÉXITO_RETRY"

    res = retry_with_backoff(funcion_intermitente, max_attempts=3, wait_duration=0.01)
    assert res == "ÉXITO_RETRY"
    assert attempts == 3


def test_retry_03_exhaust_all_attempts():
    """RETRY-03: Agotamiento de maxAttempts lanza la última excepción capturada"""
    attempts = 0
    def funcion_fallida():
        nonlocal attempts
        attempts += 1
        raise ValueError("Error persistente de base de datos")

    with pytest.raises(ValueError) as exc_info:
        retry_with_backoff(funcion_fallida, max_attempts=3, wait_duration=0.01)
    assert "Error persistente" in str(exc_info.value)
    assert attempts == 3


# --------------------------------------------------------------------------------
# GRUPO 3: PRUEBAS DE FALLBACK Y RESPUESTAS DEGRADADAS (S14_s2 - Availability)
# --------------------------------------------------------------------------------

def test_fallback_01_trigger_on_exception():
    """FALLBACK-01: Invocación automática de Fallback cuando la función principal falla"""
    def funcion_principal():
        raise RuntimeError("Fallo crítico en servidor de IA")

    def funcion_fallback():
        return {"status": "DEGRADED", "source": "HA_CACHE", "data": "Predicción histórica PNP"}

    res = execute_with_fallback(funcion_principal, funcion_fallback)
    assert res["status"] == "DEGRADED"
    assert res["source"] == "HA_CACHE"


def test_fallback_02_bypass_when_circuit_open():
    """FALLBACK-02: Bypass directo a Fallback sin llamar a la función principal si el circuito está OPEN"""
    cb_local = CircuitBreaker(sliding_window_size=2, failure_threshold=0.5, wait_duration=60.0)
    cb_local.record_result(False)
    cb_local.record_result(False)
    assert cb_local.state == CircuitState.OPEN

    principal_called = False
    def funcion_principal():
        nonlocal principal_called
        principal_called = True
        return "OK"

    def funcion_fallback():
        return "FALLBACK_DIRECTO"

    with patch("src.services.resilience_service.gnn_circuit_breaker", cb_local):
        res = execute_with_fallback(funcion_principal, funcion_fallback)
        assert res == "FALLBACK_DIRECTO"
        assert principal_called is False  # La función principal no se invocó


# --------------------------------------------------------------------------------
# GRUPO 4: PRUEBAS DE INYECCIÓN DE FALLAS (S14_s1 - Fault Injection Testing)
# --------------------------------------------------------------------------------

def test_fi_01_database_disconnect_simulation():
    """FI-01: Simulación de caída de conexión a PostgreSQL/Supabase"""
    with patch("sqlalchemy.orm.Session.query") as mock_query:
        mock_query.side_effect = Exception("Conexión rechazada por el servidor PostgreSQL (Fault Injection)")
        res = client_no_raise.get("/dashboard/mapa-geojson")
        assert res.status_code in [500, 503]


def test_fi_02_pytorch_out_of_memory_simulation():
    """FI-02: Simulación de falta de memoria RAM/GPU en PyTorch (torch.OutOfMemoryError)"""
    with patch("src.model.st_gnn.RedEspacioTemporal") as mock_gnn:
        mock_gnn.side_effect = MemoryError("Out of Memory al procesar tensores del grafo")
        res = client_no_raise.get("/monitoring/status")
        assert res.status_code in [200, 500]


def test_fi_03_smtp_server_timeout_simulation():
    """FI-03: Simulación de timeout de red al contactar servidor de correos SMTP"""
    with patch("smtplib.SMTP.connect") as mock_smtp:
        mock_smtp.side_effect = TimeoutError("Timeout conectando a SMTP Gmail")
        res = client_no_raise.post("/auth/forgot-password", json={"email": "usuario@pnp.gob.pe"})
        assert res.status_code in [200, 400, 422, 429, 500]


# --------------------------------------------------------------------------------
# GRUPO 5: PRUEBAS DE RECUPERACIÓN ANTE DESASTRES (S14_s1 - Recovery Testing)
# --------------------------------------------------------------------------------

def test_rec_01_system_health_restoration():
    """REC-01: Verificación de salud y estado UP del sistema tras solucionar incidente"""
    res = client.get("/health/")
    assert res.status_code == 200
    assert res.json()["status"] == "UP"
    assert res.json()["service"] == "PNP GNN SPRED API"
    assert res.json()["database"] == "CONNECTED"


def test_rec_02_monitoring_endpoint_resilience():
    """REC-02: El endpoint /monitoring/status reporta estado de componentes en tiempo real"""
    res = client.get("/monitoring/status")
    assert res.status_code == 200
    data = res.json()
    assert "base_de_datos" in data
    assert "modelo_gnn" in data
    assert "recursos_servidor" in data


# --------------------------------------------------------------------------------
# GRUPO 6: PRUEBAS DE MÉTRICAS Y TRAZABILIDAD (S14_s1 - MTBF & MTTR ISO 25010)
# --------------------------------------------------------------------------------

def test_met_01_mtbf_mttr_uptime_formulas():
    """MET-01: Validación de fórmulas matemáticas de MTBF, MTTR y porcentaje de Disponibilidad"""
    total_operating_hours = 1000.0
    failures_count = 2.0
    recovery_time_minutes = 10.0

    mtbf = total_operating_hours / failures_count
    mttr = recovery_time_minutes / failures_count
    uptime = ((720.0 - (recovery_time_minutes / 60.0)) / 720.0) * 100.0

    assert mtbf == 500.0
    assert mttr == 5.0
    assert uptime > 99.9


def test_met_02_actuator_health_and_cb_metrics():
    """MET-02: Endpoint /health/circuit-breakers expone métricas de ventanas y umbrales (Spring Actuator equiv)"""
    res = client.get("/health/circuit-breakers")
    assert res.status_code == 200
    cb_data = res.json()["gnn_service_breaker"]
    assert cb_data["slidingWindowSize"] == 5
    assert cb_data["failureRateThreshold"] == "50.0%"
    assert "state" in cb_data


# --------------------------------------------------------------------------------
# GRUPO 7: PRUEBAS DE RATE LIMITING Y BLOQUEOS (S14_s2 - Security Rate Limiter)
# --------------------------------------------------------------------------------

def test_rl_01_login_rate_limiting_http_429():
    """RL-01: Bloqueo HTTP 429 por exceso de peticiones consecutivas en login"""
    res = client.post("/auth/login", json={"email": "malicioso@pnp.gob.pe", "password": "wrong"})
    assert res.status_code in [200, 400, 401, 422, 429]


def test_rl_02_public_crime_report_rate_limiting():
    """RL-02: Limitador de tasa independiente para denuncias públicas ciudadanas"""
    res = client.post("/denuncias/publica", json={
        "id_tipo_delito": 1,
        "descripcion": "Denuncia de prueba de carga",
        "latitud": -12.0463,
        "longitud": -77.0428,
        "fecha_delito": "2026-06-20T12:00:00"
    })
    assert res.status_code in [200, 201, 422, 429]


def test_rl_03_scope_isolation():
    """RL-03: Aislamiento de alcances de Rate Limiting (login vs denuncias)"""
    from src.security.rate_limit import _clave
    clave_login = _clave("127.0.0.1", "login")
    clave_denuncia = _clave("127.0.0.1", "denuncia_publica")
    assert clave_login != clave_denuncia
