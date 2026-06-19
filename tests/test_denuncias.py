from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_denuncia_publica_rechazo_xss():
    """
    PRUEBA OWASP - Cross Site Scripting (XSS)
    Verifica que el middleware de validación Pydantic detecte y bloquee payloads maliciosos.
    """
    payload_malicioso = {
        "id_tipo_delito": 1,
        "fecha_delito": "2026-05-20",
        "hora_delito": "15:30:00",
        "latitud": -12.0464,
        "longitud": -77.0428,
        "descripcion": "Robo armado. <script>alert('XSS Attack')</script>"
    }
    
    response = client.post("/denuncias/publica", json=payload_malicioso)
    
    # Debe ser bloqueado por Pydantic antes de llegar a PostGIS
    assert response.status_code == 422
    error_detail = response.json().get("detail", "")
    assert isinstance(error_detail, list) or isinstance(error_detail, str)
    # Validamos que el rechazo mencione seguridad
    assert "seguridad" in str(error_detail).lower() or "bloqueado" in str(error_detail).lower()

def test_denuncia_publica_rechazo_sqli():
    """
    PRUEBA OWASP - SQL Injection (SQLi)
    Verifica que el middleware detecte palabras clave de alteración de base de datos.
    """
    payload_malicioso = {
        "id_tipo_delito": 2,
        "fecha_delito": "2026-05-20",
        "hora_delito": "16:00:00",
        "latitud": -12.0464,
        "longitud": -77.0428,
        "descripcion": "Hurto en el paradero. DROP TABLE sistema_usuarios;"
    }
    
    response = client.post("/denuncias/publica", json=payload_malicioso)
    
    assert response.status_code == 422
    error_detail = response.json().get("detail", "")
    assert "seguridad" in str(error_detail).lower() or "bloqueado" in str(error_detail).lower()

def test_denuncia_publica_valida_exitosa():
    """
    PRUEBA FUNCIONAL - Flujo Correcto
    Verifica que un reporte ciudadano legítimo sea aceptado e insertado en la cuarentena.
    """
    payload_valido = {
        "id_tipo_delito": 1,
        "fecha_delito": "2026-05-20",
        "hora_delito": "18:45:00",
        "latitud": -12.0500,
        "longitud": -77.0300,
        "descripcion": "Me arrebataron la mochila dos sujetos en moto."
    }
    
    response = client.post("/denuncias/publica", json=payload_valido)
    
    # Debe retornar 201 Created
    assert response.status_code == 201
    respuesta_json = response.json()
    assert respuesta_json["success"] is True
    assert "id" in respuesta_json
