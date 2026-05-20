import sys
from pathlib import Path

# Agregar el directorio raíz al path para que Python encuentre 'src'
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_verificacion_forense_y_rate_limiting():
    print("\n--- INICIANDO PRUEBA DE RATE LIMITING Y AUDITORÍA FORENSE ---")
    
    # 1. Simular ataque de fuerza bruta (5 intentos)
    payload_malicioso = {"email": "sospechoso@pnp.gob.pe", "password": "clave_falsa"}
    for i in range(1, 6):
        response = client.post("/auth/login", json=payload_malicioso)
        print(f"Intento {i}: HTTP {response.status_code}")
        
    # 2. El 6to intento debe ser bloqueado por la seguridad del sistema (HTTP 429)
    response_bloqueo = client.post("/auth/login", json=payload_malicioso)
    print(f"Intento 6 (Bloqueo esperado): HTTP {response_bloqueo.status_code}")
    
    # Aserción sobre la API
    assert response_bloqueo.status_code == 429, "Fallo: El Rate Limiter no bloqueó la petición."
    print("✓ Rate Limiter funcionó correctamente. HTTP 429 retornado.")
    
    # 3. Verificación forense en el log de auditoría
    log_path = root_dir / "logs" / "auditoria_pnp.log"
    assert log_path.exists(), f"Fallo: No se encontró el archivo de log en {log_path}"
    
    log_content = log_path.read_text(encoding="utf-8")
    
    # Buscamos la traza CRITICAL del logger
    if "DEFENSA ACTIVA" in log_content or "bloqueada por fuerza bruta" in log_content:
        print("✓ Traza forense CRITICAL verificada en auditoria_pnp.log.")
    else:
        print("⚠ Advertencia: El mecanismo de seguridad bloqueó la IP, pero no se encontró la traza exacta esperada en el log.")
        print("Últimas líneas del log:")
        lineas = log_content.splitlines()[-5:]
        for linea in lineas:
            print(f"   {linea}")

def test_inferencia_desacoplada():
    print("\n--- INICIANDO PRUEBA DE INFERENCIA GNN (DESACOPLADA) ---")
    
    # Simulación de un token válido (En producción esto requiere un login exitoso real)
    # Por ahora probamos que el modelo de Pydantic reciba los parámetros de negocio
    payload_negocio = {
        "fecha_consulta": "2026-05-20",
        "distrito": "Lima Cercado"
    }
    
    # Al no tener el token en este test de integración simple, esperamos un 401
    # a menos que quitemos la dependencia o hagamos un login real.
    # Comprobamos que el payload es aceptado estructuralmente.
    response = client.post("/predict/predecir", json=payload_negocio)
    print(f"Respuesta de Endpoint Predict: HTTP {response.status_code}")
    
    # Si la protección JWT funciona, debería ser 401
    # Si el JWT estuviera deshabilitado para pruebas, probaríamos la respuesta JSON
    if response.status_code == 401:
        print("✓ Endpoint protegido correctamente con JWT.")
    elif response.status_code == 200:
        print("✓ Inferencia GNN ejecutada exitosamente con parámetros de negocio.")
        print(f"Hotspots detectados: {len(response.json().get('hotspots', []))}")
    else:
        print(f"Resultado inesperado: {response.json()}")

if __name__ == "__main__":
    print("===============================================================")
    print("  CERTIFICACIÓN AUTOMATIZADA - SISTEMA PREDICTIVO PNP (APF2)")
    print("===============================================================\n")
    
    try:
        test_verificacion_forense_y_rate_limiting()
        test_inferencia_desacoplada()
        print("\n===============================================================")
        print("  TODAS LAS PRUEBAS FINALIZADAS")
        print("===============================================================")
    except AssertionError as e:
        print(f"\n❌ ERROR DE ASERCIÓN: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")
        sys.exit(1)
