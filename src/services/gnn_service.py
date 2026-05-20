import torch
import numpy as np
from fastapi import HTTPException

class GNNService:
    """
    Capa de Servicio: Aísla la lógica matemática y de PyTorch del controlador web.
    """
    @staticmethod
    def ejecutar_inferencia(
        ventana_historica: list, 
        top_k: int, 
        umbral: float, 
        ml_models: dict, 
        device: torch.device
    ) -> list:
        
        if "gnn" not in ml_models:
            raise HTTPException(status_code=500, detail="El cerebro de la IA no está instanciado en memoria.")
            
        try:
            # 1. Preparación de Tensores
            x_input = torch.tensor(ventana_historica, dtype=torch.float32)
            if x_input.ndim == 3:
                x_input = x_input.unsqueeze(0) 
                
            if x_input.shape != (1, 14, 400, 5):
                raise ValueError(f"Matriz inválida. Se esperaba [14, 400, 5], llegó {list(x_input.shape[1:])}")
                
            x_input = x_input.to(device)
            
            # 2. Inferencia Pura
            modelo = ml_models["gnn"]
            edge_index = ml_models["edge_index"]
            edge_weights = ml_models["edge_weights"]
            
            with torch.no_grad():
                predicciones = modelo(x_input, edge_index, edge_weights)
                predicciones_array = predicciones.squeeze(0).cpu().numpy()
                
            predicciones_array = np.maximum(predicciones_array, 0)
            
            # 3. Lógica de Negocio (Semáforo Policial)
            alertas_grilla = []
            for nodo_id, score in enumerate(predicciones_array):
                score_float = float(score)
                
                if score_float < umbral:
                    estado_semaforo = "Verde"
                elif score_float >= umbral and score_float < (umbral * 10):
                    estado_semaforo = "Amarilla"
                else:
                    estado_semaforo = "Roja" 
                    
                alertas_grilla.append({
                    "id_nodo": nodo_id,
                    "score_densidad_delictiva": score_float,
                    "alerta_patrullaje": estado_semaforo
                })
                
            # 4. Filtrado Top-K
            alertas_ordenadas = sorted(alertas_grilla, key=lambda x: x["score_densidad_delictiva"], reverse=True)
            hotspots_prioritarios = [a for a in alertas_ordenadas if a["alerta_patrullaje"] != "Verde"][:top_k]
            
            return hotspots_prioritarios
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Fallo proprocesal en GNN: {str(e)}")