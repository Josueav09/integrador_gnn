import os
import json
import torch
import numpy as np
from fastapi import HTTPException
from datetime import datetime, timedelta
from sqlalchemy import text
from src.core.database import SessionLocal

class GNNService:
    """
    Capa de Servicio: Aísla la lógica matemática y de PyTorch del controlador web.
    Usa datos reales de delitos y topología cargados desde archivos y base de datos.
    """
    _tensor_panel = None
    _panel_dates = None
    _date_to_idx = None
    _quadrant_coords = None

    @classmethod
    def _inicializar_recursos(cls):
        if cls._tensor_panel is None:
            # Directorio base del proyecto
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            tensor_path = os.path.join(base_dir, "src", "model", "tensor_panel.npy")
            dates_path = os.path.join(base_dir, "src", "model", "panel_dates.json")
            
            # Cargar tensor e índice de fechas
            if not os.path.exists(tensor_path) or not os.path.exists(dates_path):
                raise FileNotFoundError(
                    f"Recursos GNN no encontrados en src/model/. Asegúrese de haber corrido los scripts de exportación."
                )
                
            cls._tensor_panel = np.load(tensor_path)  # Shape: (1551, 400, 5)
            with open(dates_path, 'r', encoding='utf-8') as f:
                cls._panel_dates = json.load(f)
                
            cls._date_to_idx = {d: idx for idx, d in enumerate(cls._panel_dates)}
            
        if cls._quadrant_coords is None:
            # Consultar base de datos una sola vez para mapear id_cuadrante a coords y distrito
            db = SessionLocal()
            try:
                rows = db.execute(text("""
                    SELECT q.id_cuadrante, d.nombre_distrito, ST_Y(q.centroide) as lat, ST_X(q.centroide) as lng
                    FROM cuadrantes q
                    JOIN distritos d ON q.id_distrito = d.id_distrito
                """)).all()
                cls._quadrant_coords = {
                    int(row[0]): {
                        "distrito": row[1].strip().upper(),
                        "lat": float(row[2]) if row[2] else 0.0,
                        "lng": float(row[3]) if row[3] else 0.0
                    }
                    for row in rows
                }
            except Exception as e:
                print(f"[GNNService - WARNING] Fallo al cargar cuadrantes de la BD: {e}")
                cls._quadrant_coords = {}
            finally:
                db.close()

    @staticmethod
    def ejecutar_inferencia(
        fecha_consulta: str, 
        tipo_delito: str,
        top_k: int, 
        umbral: float, 
        ml_models: dict, 
        device: torch.device,
        nodos_validos: list
    ) -> list:
        
        if "gnn" not in ml_models:
            raise HTTPException(status_code=500, detail="El cerebro de la GNN no está instanciado en memoria.")
            
        try:
            # Inicializar recursos estáticos de forma lazy
            GNNService._inicializar_recursos()
            
            # 1. Obtener ventana histórica de 14 días
            if fecha_consulta in GNNService._date_to_idx:
                # Si la fecha existe en el dataset (2022-01-01 a 2026-03-31), usamos la ventana real
                idx = GNNService._date_to_idx[fecha_consulta]
                # Para predecir para el día idx, necesitamos la ventana [idx - 14 : idx]
                if idx < 14:
                    # Fallback si no hay suficiente historia al inicio
                    window = GNNService._tensor_panel[0:14].copy()
                else:
                    window = GNNService._tensor_panel[idx - 14 : idx].copy()
            else:
                # Si la fecha es externa (ej: 2026-05-20), usamos los últimos conteos de delitos,
                # pero construimos las variables temporales dinámicamente para la nueva fecha
                counts_history = GNNService._tensor_panel[-14:, :, 0].copy()  # (14, 400)
                
                # Construir secuencia de 14 días terminando el día anterior a la consulta
                dt_consulta = datetime.strptime(fecha_consulta, "%Y-%m-%d")
                window = np.zeros((14, 400, 5), dtype=np.float32)
                
                for i in range(14):
                    d_i = dt_consulta - timedelta(days=14 - i)
                    dia_semana = d_i.weekday()
                    es_fin_semana = 1.0 if dia_semana >= 5 else 0.0
                    mes_sin = np.sin(2 * np.pi * d_i.month / 12.0)
                    mes_cos = np.cos(2 * np.pi * d_i.month / 12.0)
                    
                    window[i, :, 0] = counts_history[i]
                    window[i, :, 1] = dia_semana
                    window[i, :, 2] = es_fin_semana
                    window[i, :, 3] = mes_sin
                    window[i, :, 4] = mes_cos
            
            # 2. Escalamiento MinMax de la característica 0 (conteo_delitos)
            # El scaler de train fue calibrado de 0 a 15.0
            window[:, :, 0] = np.clip(window[:, :, 0] / 15.0, 0.0, 1.0)
            
            # 3. Conversión a Tensor PyTorch
            x_input = torch.tensor(window, dtype=torch.float32).unsqueeze(0).to(device)  # [1, 14, 400, 5]
            
            # 4. Inferencia del Modelo GNN
            modelo = ml_models["gnn"]
            edge_index = ml_models["edge_index"]
            edge_weights = ml_models["edge_weights"]
            
            with torch.no_grad():
                predicciones = modelo(x_input, edge_index, edge_weights)
                predicciones_array = predicciones.squeeze(0).cpu().numpy()
            
            # 5. Filtrado Bayesiano y Formateo
            probabilidad_condicional = 1.0
            if tipo_delito == 'ROB-001':
                probabilidad_condicional = 0.65  # Ponderador histórico para Robos
            elif tipo_delito == 'HUR-001':
                probabilidad_condicional = 0.35  # Ponderador histórico para Hurtos
                
            alertas_grilla = []
            for nodo_id, score in enumerate(predicciones_array):
                db_id = int(nodo_id) + 1  # Base de datos es 1-indexed (1 a 400)
                
                # Filtrado por enmascaramiento de distrito (distrito_nombre)
                if nodos_validos is not None and db_id not in nodos_validos:
                    continue
                    
                score_float = float(score) * probabilidad_condicional
                
                # Semáforo Policial
                if score_float < umbral:
                    estado_semaforo = "Verde"
                elif score_float >= umbral and score_float < (umbral * 10):
                    estado_semaforo = "Amarilla"
                else:
                    estado_semaforo = "Roja"
                    
                # Obtener coordenadas y distrito reales desde caché
                q_info = GNNService._quadrant_coords.get(db_id, {"distrito": "DESCONOCIDO", "lat": 0.0, "lng": 0.0})
                
                alertas_grilla.append({
                    "id_nodo": int(nodo_id),
                    "score_densidad_delictiva": score_float,
                    "alerta_patrullaje": estado_semaforo,
                    "lat": q_info["lat"],
                    "lng": q_info["lng"],
                    "distrito": q_info["distrito"]
                })
                
            # 6. Ordenar por riesgo y aplicar Top-K
            alertas_ordenadas = sorted(alertas_grilla, key=lambda x: x["score_densidad_delictiva"], reverse=True)
            hotspots_prioritarios = [a for a in alertas_ordenadas if a["alerta_patrullaje"] != "Verde"][:top_k]
            
            return hotspots_prioritarios
            
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Fallo en procesamiento GNN: {str(e)}")