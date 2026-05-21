import torch
import numpy as np
from fastapi import HTTPException
from datetime import datetime

class GNNService:
    """
    Capa de Servicio: Aísla la lógica matemática y de PyTorch del controlador web.
    Maneja el caché asíncrono para evitar cuellos de botella en DB.
    """
    # Buffer asíncrono en RAM para la ventana histórica (14 días x 400 nodos x 3 features base)
    # En producción esto se poblaría mediante un Job planificado consultando a PostgreSQL/Redis.
    _cache_historico = None
    
    @classmethod
    def _obtener_buffer_historico(cls) -> torch.Tensor:
        if cls._cache_historico is None:
            # Simulación de carga desde PostgreSQL para los 400 micro-cuadrantes
            # [14 días, 400 nodos, 3 features: delitos_acumulados, KDE_previo, densidad_vial]
            cls._cache_historico = torch.rand((14, 400, 3), dtype=torch.float32)
        return cls._cache_historico.clone()

    @staticmethod
    def ejecutar_inferencia(
        fecha_consulta: str, 
        distrito: str,
        tipo_delito: str,
        top_k: int, 
        umbral: float, 
        ml_models: dict, 
        device: torch.device
    ) -> list:
        
        if "gnn" not in ml_models:
            raise HTTPException(status_code=500, detail="El cerebro de la IA no está instanciado en memoria.")
            
        try:
            # 1. Preparación de Tensores y Desacoplamiento
            # Obtenemos el buffer base (14, 400, 3)
            base_tensor = GNNService._obtener_buffer_historico()
            
            # Extraemos atributos de fecha para la ingeniería de features dinámica
            dt = datetime.strptime(fecha_consulta, "%Y-%m-%d")
            dia_semana = dt.weekday()
            
            # Inyección de features temporales dinámicos (Ej: sin_tiempo, cos_tiempo, feriado)
            # Para coincidir con la arquitectura [14, 400, 5], agregamos 2 canales adicionales.
            canal_temporal_1 = torch.full((14, 400, 1), float(np.sin(2 * np.pi * dia_semana / 7.0)))
            canal_temporal_2 = torch.full((14, 400, 1), float(np.cos(2 * np.pi * dia_semana / 7.0)))
            
            x_input = torch.cat([base_tensor, canal_temporal_1, canal_temporal_2], dim=2)
            x_input = x_input.unsqueeze(0).to(device) # [1, 14, 400, 5]
            
            # 2. Inferencia Pura
            modelo = ml_models["gnn"]
            edge_index = ml_models["edge_index"]
            edge_weights = ml_models["edge_weights"]
            
            with torch.no_grad():
                predicciones = modelo(x_input, edge_index, edge_weights)
                predicciones_array = predicciones.squeeze(0).cpu().numpy()
            
            # Nota: La activación Softplus en el modelo ya garantiza la no-negatividad.
            
            # --- APROXIMACIÓN HEURÍSTICA DE INDEPENDENCIA CONDICIONAL (APF2) ---
            # El modelo predice la "Temperatura Criminal" global. 
            # Asumimos independencia condicional: P(Delito | Grilla) = P(Riesgo_Global) * P(Delito_Histórico)
            probabilidad_condicional = 1.0
            if tipo_delito == 'ROB-001':
                probabilidad_condicional = 0.65  # Ponderador histórico Bayesiano para Robos
            elif tipo_delito == 'HUR-001':
                probabilidad_condicional = 0.35  # Ponderador histórico Bayesiano para Hurtos
            
            # 3. Lógica de Negocio (Semáforo Policial)
            alertas_grilla = []
            for nodo_id, score in enumerate(predicciones_array):
                # Aplicamos el filtro Bayesiano
                score_float = float(score) * probabilidad_condicional
                
                if score_float < umbral:
                    estado_semaforo = "Verde"
                elif score_float >= umbral and score_float < (umbral * 10):
                    estado_semaforo = "Amarilla"
                else:
                    estado_semaforo = "Roja" 
                    
                alertas_grilla.append({
                    "id_nodo": int(nodo_id),
                    "score_densidad_delictiva": float(score_float),
                    "alerta_patrullaje": str(estado_semaforo)
                })
                
            # 4. Filtrado Top-K
            alertas_ordenadas = sorted(alertas_grilla, key=lambda x: x["score_densidad_delictiva"], reverse=True)
            hotspots_prioritarios = [a for a in alertas_ordenadas if a["alerta_patrullaje"] != "Verde"][:top_k]
            
            return hotspots_prioritarios
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Fallo en procesamiento GNN: {str(e)}")