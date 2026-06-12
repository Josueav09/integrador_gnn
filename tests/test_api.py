import time
import os
import requests
import numpy as np

print("=== SIMULADOR DE FRONTEND (REACT) ===")
print("Generando trama de datos espaciotemporales (14 días históricos para 400 cuadrantes)...")
# Creamos un tensor simulado (valores entre 0 y 1 imitando sus datos escalados)
datos_simulados = np.random.rand(14, 400, 5).tolist()

payload = {
    "ventana_historica": datos_simulados
}

# Cargar API_URL dinámicamente de variables de entorno
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")

print(f"Enviando petición HTTP POST al Monolito FastAPI en {API_URL}...")
# Pedimos explícitamente el Top 5 para probar la lógica contra la Fatiga de Alarma
inicio = time.time()
respuesta = requests.post(f"{API_URL}/predecir?top_k=5", json=payload)
fin = time.time()

latencia_ms = (fin - inicio) * 1000

if respuesta.status_code == 200:
    data = respuesta.json()
    print(f"\n=== RESPUESTA TÁCTICA RECIBIDA ===")
    print(f"Estado: {data['status']}")
    
    print(f"\nHotspots priorizados enviados a la PNP (Top {data['metricas_despliegue']['limite_top_k_solicitado']}):")
    for hotspot in data['hotspots']:
        print(f" - Cuadrante ID {hotspot['id_nodo']}: Alerta {hotspot['alerta_patrullaje']} (Peligro: {hotspot['score_densidad_delictiva']:.4f})")
    
    print(f"\n[MÉTRICA SLA] Latencia extremo a extremo: {latencia_ms:.2f} milisegundos")
    
    if latencia_ms < 500:
        print("[ÉXITO] ¡El sistema aprueba el SLA de la PNP (< 500ms)!")
    else:
        print("[ALERTA] La latencia superó el umbral estricto.")
else:
    print(f"[ERROR FATAL] Código {respuesta.status_code}: {respuesta.text}")