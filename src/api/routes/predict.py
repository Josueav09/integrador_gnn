from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.security.jwt_handler import get_current_user
from src.services.gnn_service import GNNService

router = APIRouter(prefix="/predict", tags=["Predicciones GNN"])

class ConsultaPredictiva(BaseModel):
    fecha_consulta: str  # Formato 'YYYY-MM-DD'
    distrito: str
    tipo_delito: str = "TODOS" # ROB-001, HUR-001, TODOS

@router.post("/predecir")
async def ejecutar_prediccion(
    consulta: ConsultaPredictiva, 
    top_k: int = 50,
    token: dict = Depends(get_current_user)
):
    """
    ENDPOINT CORE: Controlador limpio que delega la inferencia a la capa de Servicios.
    Recibe parámetros de negocio, el backend construye el tensor internamente.
    """
    # Importamos las variables de memoria global
    from src.api.main import ml_models, hardware_device, UMBRAL_PNP

    # Delegamos el cálculo complejo al Servicio GNN
    hotspots_prioritarios = GNNService.ejecutar_inferencia(
        fecha_consulta=consulta.fecha_consulta,
        distrito=consulta.distrito,
        tipo_delito=consulta.tipo_delito,
        top_k=top_k,
        umbral=UMBRAL_PNP,
        ml_models=ml_models,
        device=hardware_device
    )
    
    return {
        "status": "success",
        "agente_solicitante": int(token["user_id"]) if isinstance(token.get("user_id"), (int, float, str)) else str(token.get("user_id")), 
        "metricas_despliegue": {
            "hotspots_enviados_a_pnp": int(len(hotspots_prioritarios)),
        },
        "hotspots": hotspots_prioritarios
    }