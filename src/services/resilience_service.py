import time
from enum import Enum
from typing import Callable, Any
from src.utils.logger import logger


class CircuitState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"


class CircuitBreaker:
    """
    Implementación del Patrón Circuit Breaker según la norma ISO 25010 y S14_s2.
    Parámetros:
    - sliding_window_size: Número de llamadas analizadas en la ventana deslizante (5 por defecto).
    - failure_threshold: Porcentaje máximo de errores para abrir el circuito (50% por defecto).
    - wait_duration: Tiempo de espera en estado OPEN antes de pasar a HALF_OPEN (10s por defecto).
    - permitted_half_open_calls: Llamadas de prueba permitidas en HALF_OPEN (2 por defecto).
    """

    def __init__(
        self,
        sliding_window_size: int = 5,
        failure_threshold: float = 0.5,
        wait_duration: float = 10.0,
        permitted_half_open_calls: int = 2,
    ):
        self.sliding_window_size = sliding_window_size
        self.failure_threshold = failure_threshold
        self.wait_duration = wait_duration
        self.permitted_half_open_calls = permitted_half_open_calls
        self.state = CircuitState.CLOSED
        self.history: list[bool] = []  # True = Éxito, False = Fallo
        self.last_state_change = time.time()
        self.half_open_successes = 0

    def can_execute(self) -> bool:
        now = time.time()
        if self.state == CircuitState.OPEN:
            if now - self.last_state_change > self.wait_duration:
                self.state = CircuitState.HALF_OPEN
                self.last_state_change = now
                self.half_open_successes = 0
                logger.info("CircuitBreaker: Transición a HALF_OPEN. Probando salud del servicio...")
                return True
            return False
        return True

    def record_result(self, success: bool):
        if self.state == CircuitState.HALF_OPEN:
            if success:
                self.half_open_successes += 1
                if self.half_open_successes >= self.permitted_half_open_calls:
                    self.state = CircuitState.CLOSED
                    self.history.clear()
                    logger.info("CircuitBreaker: Restablecido con éxito a CLOSED")
            else:
                self.state = CircuitState.OPEN
                self.last_state_change = time.time()
                logger.warning("CircuitBreaker: Fallo detectado en HALF_OPEN. Regresando a OPEN")
            return

        self.history.append(success)
        if len(self.history) > self.sliding_window_size:
            self.history.pop(0)

        if len(self.history) == self.sliding_window_size:
            failures = self.history.count(False)
            failure_rate = failures / self.sliding_window_size
            if failure_rate >= self.failure_threshold:
                self.state = CircuitState.OPEN
                self.last_state_change = time.time()
                logger.error(f"CircuitBreaker: Circuito ABIERTO (OPEN). Tasa de fallas: {failure_rate*100}%")


# Instancia global del cortocircuito para el modelo de IA GNN y servicios críticos
gnn_circuit_breaker = CircuitBreaker()


def execute_with_fallback(func: Callable, fallback_func: Callable, *args, **kwargs) -> Any:
    """
    Ejecuta una función protegida por Circuit Breaker con respuesta degradada (Fallback).
    """
    if not gnn_circuit_breaker.can_execute():
        logger.warning("CircuitBreaker [OPEN]: Invocando respuesta de emergencia (Fallback)...")
        return fallback_func(*args, **kwargs)
    try:
        result = func(*args, **kwargs)
        gnn_circuit_breaker.record_result(True)
        return result
    except Exception as ex:
        logger.error(f"Error en ejecución de servicio: {ex}")
        gnn_circuit_breaker.record_result(False)
        return fallback_func(*args, **kwargs)


def retry_with_backoff(func: Callable, max_attempts: int = 3, wait_duration: float = 0.5, *args, **kwargs) -> Any:
    """
    Patrón Retry con espera incremental (Backoff) según S14_s2.
    """
    last_exception = None
    for attempt in range(1, max_attempts + 1):
        try:
            return func(*args, **kwargs)
        except Exception as ex:
            last_exception = ex
            logger.warning(f"Intento {attempt}/{max_attempts} fallido: {ex}. Reintentando en {wait_duration}s...")
            time.sleep(wait_duration)
    raise last_exception
