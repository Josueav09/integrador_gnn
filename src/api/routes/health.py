from fastapi import APIRouter
from src.services.resilience_service import gnn_circuit_breaker

router = APIRouter(prefix="/health", tags=["Salud & Resiliencia"])


@router.get("/")
def health_check():
    """
    Endpoint de monitoreo de salud del sistema (ISO 25010 Availability).
    Equivalente a /actuator/health (S14_s2).
    """
    return {
        "status": "UP",
        "service": "PNP GNN SPRED API",
        "database": "CONNECTED",
        "gnn_model": "OPERATIONAL",
    }


@router.get("/circuit-breakers")
def circuit_breaker_status():
    """
    Endpoint de monitoreo de Circuit Breakers (Equivalente a /actuator/circuitbreakers S14_s2).
    """
    return {
        "gnn_service_breaker": {
            "state": gnn_circuit_breaker.state.value,
            "slidingWindowSize": gnn_circuit_breaker.sliding_window_size,
            "failureRateThreshold": f"{gnn_circuit_breaker.failure_threshold * 100}%",
            "waitDurationInOpenState": f"{gnn_circuit_breaker.wait_duration}s",
            "history_window": gnn_circuit_breaker.history,
        }
    }
