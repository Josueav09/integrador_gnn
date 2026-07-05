"""
Certificación de seguridad APF3 — alineado al Anexo D del informe del equipo.
Ejecutar: pytest tests/test_security_robustness.py -v -s
"""
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from src.api.main import app
from src.security.rate_limit import registro_ips

client = TestClient(app)


@pytest.fixture(autouse=True)
def limpiar_rate_limit():
    registro_ips.clear()
    yield
    registro_ips.clear()


def test_bloqueo_fuerza_bruta_login_http_429():
    payload = {"email": "sospechoso@pnp.gob.pe", "password": "clave_falsa"}
    for _ in range(5):
        client.post("/auth/login", json=payload)
    response = client.post("/auth/login", json=payload)
    assert response.status_code == 429


def test_rate_limit_forgot_password_spam_smtp():
    payload = {"email": "analista@pnp.gob.pe"}
    for _ in range(5):
        client.post("/auth/forgot-password", json=payload)
    response = client.post("/auth/forgot-password", json=payload)
    assert response.status_code == 429


def test_rate_limit_verify_code_pin():
    payload = {"email": "analista@pnp.gob.pe", "code": "000000"}
    for _ in range(5):
        client.post("/auth/verify-code", json=payload)
    response = client.post("/auth/verify-code", json=payload)
    assert response.status_code == 429


def test_bloqueo_sqli_denuncia_publica():
    payload = {
        "id_tipo_delito": 1,
        "fecha_delito": "2026-06-16",
        "hora_delito": "10:00:00",
        "latitud": -12.0464,
        "longitud": -77.0428,
        "descripcion": "Intento DROP TABLE sistema_usuarios;",
    }
    response = client.post("/denuncias/publica", json=payload)
    assert response.status_code == 422
    assert "seguridad" in str(response.json()).lower()


def test_bloqueo_xss_denuncia_publica():
    payload = {
        "id_tipo_delito": 1,
        "fecha_delito": "2026-06-16",
        "hora_delito": "10:00:00",
        "latitud": -12.0464,
        "longitud": -77.0428,
        "descripcion": "<script>alert('xss')</script>",
    }
    response = client.post("/denuncias/publica", json=payload)
    assert response.status_code == 422
    assert "seguridad" in str(response.json()).lower()
