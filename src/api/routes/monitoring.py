import time
import os
import platform
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
import torch

from src.core.database import get_db
from src.security.rate_limit import registro_ips
from src.utils.logger import logger

router = APIRouter(prefix="/monitoring", tags=["Monitoreo de Sistema"])

@router.get("/status")
def get_monitoring_status(db: Session = Depends(get_db)):
    """
    Endpoint de Monitoreo en Tiempo Real.
    Verifica la salud de la base de datos, del modelo GNN y del uso básico de recursos.
    """
    status_db = "DESCONECTADO"
    latencia_db_ms = None
    
    # 1. Medir latencia de conexión a Base de Datos (Supabase/Local)
    try:
        start_time = time.time()
        db.execute(text("SELECT 1"))
        latencia_db_ms = round((time.time() - start_time) * 1000, 2)
        status_db = "CONECTADO"
    except Exception as e:
        logger.error(f"[MONITOREO] Error de conexión a BD: {str(e)}")
        status_db = "ERROR"

    # 2. Verificar estado de la Inteligencia Artificial (GNN)
    # Evitamos importación circular importando localmente
    from src.api.main import ml_models, hardware_device
    
    gnn_cargado = "gnn" in ml_models
    edge_index_cargado = "edge_index" in ml_models
    edge_weights_cargado = "edge_weights" in ml_models
    
    status_ia = "OPERATIVO" if (gnn_cargado and edge_index_cargado and edge_weights_cargado) else "INACTIVO"
    
    # 3. Intentar obtener el uso de CPU y memoria usando psutil
    cpu_percent = None
    memory_use_mb = None
    try:
        import psutil
        process = psutil.Process(os.getpid())
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory_use_mb = round(process.memory_info().rss / (1024 * 1024), 2)
    except ImportError:
        # Fallback si psutil no está instalado
        cpu_percent = "N/A (psutil no instalado)"
        memory_use_mb = "N/A (psutil no instalado)"
    except Exception as e:
        logger.warning(f"[MONITOREO] Error leyendo recursos con psutil: {str(e)}")
        cpu_percent = "Error"
        memory_use_mb = "Error"

    # 4. Estadísticas del Rate Limiting (Seguridad)
    ips_bloqueadas_count = sum(
        1 for ip, datos in registro_ips.items() 
        if datos.get("bloqueado_hasta", 0) > time.time()
    )
    
    # 5. Información del Sistema Operativo
    so_info = f"{platform.system()} {platform.release()}"

    return {
        "status": "ok" if (status_db == "CONECTADO" and status_ia == "OPERATIVO") else "unhealthy",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "sistema_operativo": so_info,
        "base_de_datos": {
            "estado": status_db,
            "latencia_ms": latencia_db_ms
        },
        "modelo_gnn": {
            "estado": status_ia,
            "dispositivo": str(hardware_device),
            "pesos_cargados": gnn_cargado,
            "grafo_nodos_cargado": edge_index_cargado
        },
        "seguridad": {
            "ips_bloqueadas_activas": ips_bloqueadas_count,
            "total_ips_registradas": len(registro_ips)
        },
        "recursos_servidor": {
            "cpu_uso_porcentaje": cpu_percent,
            "memoria_rss_mb": memory_use_mb
        }
    }
