import requests
import random
import time

API_URL = "http://localhost:8000"

def simular_peticion_frontend():
    print("=== INICIANDO SIMULACIÓN DE CLIENTE (FRONTEND) ===")
    
    # 1. Hacer Login
    print("1. Autenticando con la API (Obteniendo JWT)...")
    login_data = {"email": "admin@pnp.gob.pe", "password": "TesisUTP2026*"}
    res_login = requests.post(f"{API_URL}/auth/login", json=login_data)
    
    if res_login.status_code != 200:
        print(f"Error en login: {res_login.text}")
        return
        
    token = res_login.json().get("access_token")
    print(f"[OK] Token JWT capturado exitosamente.")
    
    # 2. Generar Matriz Falsa 
    print("2. Generando matriz espaciotemporal [14 días x 400 nodos x 5 variables]...")
    inicio = time.time()
    # Usamos random para simular la intensidad delictiva (0.0 a 1.0)
    matriz_historica = [[[random.random() for _ in range(5)] for _ in range(400)] for _ in range(14)]
    print(f"[OK] Matriz de 28,000 elementos generada en {round(time.time() - inicio, 3)} segundos.")
    
    # 3. Disparar predicción
    print("3. Consultando al Cerebro GNN de la API...")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"ventana_historica": matriz_historica}
    
    res_predict = requests.post(f"{API_URL}/predict/predecir?top_k=5", json=payload, headers=headers)
    
    print("\n=== RESPUESTA DEL SISTEMA POLICIAL ===")
    if res_predict.status_code == 200:
        data = res_predict.json()
        print(f"Status: {data['status']}")
        print(f"Agente: {data['agente_solicitante']}")
        print(f"Métricas: {data['metricas_despliegue']}")
        print("\nTOP 5 ZONAS ROJAS (HOTSPOTS):")
        for alerta in data['hotspots']:
            print(f" - Cuadrante ID: {alerta['id_nodo']} | Peligrosidad: {round(alerta['score_densidad_delictiva'], 4)} | Semáforo: {alerta['alerta_patrullaje']}")
    else:
        print(f"Error de la API: {res_predict.text}")

if __name__ == "__main__":
    simular_peticion_frontend()