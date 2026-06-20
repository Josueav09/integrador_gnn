import sys
from pathlib import Path

# Agregar el directorio raíz al path para que Python encuentre 'src'
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from fastapi.testclient import TestClient
from src.api.main import app
from src.security.rate_limit import registro_ips

client = TestClient(app)

def test_login_brute_force_blocking():
    """Prueba que tras 5 intentos fallidos de login desde la misma IP, se bloquee con 429."""
    # Limpiamos registro de IPs para garantizar consistencia en la prueba
    registro_ips.clear()
    
    payload_erroneo = {"email": "no_existe_agente@pnp.gob.pe", "password": "incorrect_password"}
    
    # 1. Ejecutar 5 intentos fallidos
    for i in range(1, 6):
        response = client.post("/auth/login", json=payload_erroneo)
        assert response.status_code == 401, f"Intento {i} debió fallar con 401."
        
    # 2. El 6to intento debe recibir un HTTP 429
    response_bloqueado = client.post("/auth/login", json=payload_erroneo)
    assert response_bloqueado.status_code == 429, "El 6to intento debió retornar HTTP 429 por bloqueo de reintentos."
    assert "Demasiados intentos fallidos" in response_bloqueado.json()["detail"]
    print("[OK] Confirmado: Bloqueo de fuerza bruta para inicio de sesion (HTTP 429).")

def test_forgot_password_rate_limiting():
    """Prueba que forgot-password penaliza intentos sospechosos de recuperación (correo inactivo o inexistente)."""
    registro_ips.clear()
    
    payload = {"email": "correo_inexistente_sospechoso@pnp.gob.pe"}
    
    # Intentos a forgot-password
    for i in range(1, 6):
        response = client.post("/auth/forgot-password", json=payload)
        # Siempre responde success: True para evitar enumeración, pero acumula fallas
        assert response.status_code == 200
        
    # El 6to intento debe dar 429
    response_bloqueado = client.post("/auth/forgot-password", json=payload)
    assert response_bloqueado.status_code == 429, "El 6to intento debió bloquearse con HTTP 429."
    print("[OK] Confirmado: Rate Limiting en forgot-password para mitigar spam SMTP.")

def test_verify_code_brute_force_blocking():
    """Prueba que verify-code bloquea IPs que intenten adivinar el PIN de 6 dígitos."""
    registro_ips.clear()
    
    payload = {"email": "admin@pnp.gob.pe", "code": "000000"} # PIN erróneo
    
    for i in range(1, 6):
        response = client.post("/auth/verify-code", json=payload)
        assert response.status_code == 400, "Debió fallar con 400 (PIN incorrecto)."
        
    response_bloqueado = client.post("/auth/verify-code", json=payload)
    assert response_bloqueado.status_code == 429, "El 6to intento debió retornar HTTP 429."
    print("[OK] Confirmado: Defensa activa contra fuerza bruta de PIN en verify-code.")

def test_sql_injection_mitigation():
    """Prueba la detección y rechazo de payloads de inyección SQL (SQLi)."""
    # En denuncias.py validamos la descripción de denuncia contra SQLi
    payload_sqli = {
        "id_tipo_delito": 1,
        "fecha_delito": "2026-06-19",
        "hora_delito": "12:00:00",
        "latitud": -12.0463,
        "longitud": -77.0312,
        "descripcion": "Robo a mano armada UNION SELECT * FROM usuarios"
    }
    
    response = client.post("/denuncias/publica", json=payload_sqli)
    assert response.status_code == 422, "El endpoint debió rechazar la inyección SQL (HTTP 422)."
    assert "seguridad" in response.text or "SQLi" in response.text
    print("[OK] Confirmado: Bloqueo activo de inyeccion SQL (SQLi) mediante sanitizacion de Pydantic.")

def test_xss_mitigation():
    """Prueba la detección y neutralización de payloads de Cross-Site Scripting (XSS)."""
    payload_xss = {
        "id_tipo_delito": 1,
        "fecha_delito": "2026-06-19",
        "hora_delito": "12:00:00",
        "latitud": -12.0463,
        "longitud": -77.0312,
        "descripcion": "Delito reportado <script>alert('Ataque XSS')</script>"
    }
    
    response = client.post("/denuncias/publica", json=payload_xss)
    assert response.status_code == 422, "El endpoint debió rechazar el payload XSS (HTTP 422)."
    assert "seguridad" in response.text or "XSS" in response.text
    print("[OK] Confirmado: Bloqueo activo de inyeccion script HTML/JS (XSS).")

if __name__ == "__main__":
    print("=== EJECUTANDO CERTIFICACION DE SEGURIDAD INTERNA ===")
    test_login_brute_force_blocking()
    test_forgot_password_rate_limiting()
    test_verify_code_brute_force_blocking()
    test_sql_injection_mitigation()
    test_xss_mitigation()
    print("=== TODAS LAS PRUEBAS DE SEGURIDAD PASARON CORRECTAMENTE ===")
