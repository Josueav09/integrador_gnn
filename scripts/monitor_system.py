import sys
import os
import time
import urllib.request
import json
from pathlib import Path

# Configurar rutas
script_dir = Path(__file__).resolve().parent
backend_dir = script_dir.parent
log_file_path = backend_dir / "logs" / "monitoreo_reporte.txt"

# Crear carpeta de logs si no existe
log_file_path.parent.mkdir(exist_ok=True)

TARGET_URL = os.environ.get("MONITOR_URL", "http://localhost:8000/monitoring/status")

def ejecutar_monitoreo():
    print(f"=== INICIANDO SCRIPT DE MONITOREO DE SISTEMA (EVIDENCIA) ===")
    print(f"Objetivo: {TARGET_URL}")
    print(f"Buscando reporte en: {log_file_path}\n")
    
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"Fecha/Hora: {timestamp} | "
    
    try:
        # Enviar una petición HTTP GET con timeout de 5 segundos
        req = urllib.request.Request(TARGET_URL)
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            status = data.get("status", "unknown")
            latencia_db = data.get("base_de_datos", {}).get("latencia_ms", "N/A")
            dispositivo_ia = data.get("modelo_gnn", {}).get("dispositivo", "N/A")
            ia_estado = data.get("modelo_gnn", {}).get("estado", "N/A")
            ips_bloqueadas = data.get("seguridad", {}).get("ips_bloqueadas_activas", 0)
            cpu_uso = data.get("recursos_servidor", {}).get("cpu_uso_porcentaje", "N/A")
            memoria = data.get("recursos_servidor", {}).get("memoria_rss_mb", "N/A")
            
            # Formatear la línea de reporte
            resultado = (
                f"ESTADO: {status} | BD Latencia: {latencia_db}ms | "
                f"IA Estado: {ia_estado} ({dispositivo_ia}) | IPs Bloqueadas: {ips_bloqueadas} | "
                f"CPU: {cpu_uso}% | Mem: {memoria}MB"
            )
            print(f"[OK] {resultado}")
            log_entry += f"[SUCCESS] {resultado}\n"
            
    except Exception as e:
        error_msg = f"ESTADO: OFFLINE/ERROR | Detalle: {str(e)}"
        print(f"[CRÍTICO] {error_msg}")
        log_entry += f"[CRITICAL] {error_msg}\n"
        
    # Escribir la traza de monitoreo al archivo de evidencia física
    with open(log_file_path, "a", encoding="utf-8") as f:
        f.write(log_entry)
        
    print(f"\nReporte registrado correctamente en '{log_file_path.name}'.")

if __name__ == "__main__":
    ejecutar_monitoreo()
