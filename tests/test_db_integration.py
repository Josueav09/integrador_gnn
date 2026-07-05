"""
Pruebas de integración con Supabase (PostGIS) y cola SMTP asíncrona.
Ejecutar: pytest tests/test_db_integration.py -v
Requiere DATABASE_URL configurado; si no hay BD, los tests se omiten.
"""
import os
import sys
import time
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

pytestmark = pytest.mark.skipif(
    not os.getenv("DATABASE_URL"),
    reason="DATABASE_URL no configurado — omitiendo integración Supabase",
)

from src.api.main import app
from src.core.database import SessionLocal

client = TestClient(app)


def test_database_handshake():
    """RTT de lectura en Supabase/PostgreSQL."""
    inicio = time.perf_counter()
    db = SessionLocal()
    try:
        filas = db.execute(text("SELECT id_rol, nombre_rol FROM sistema_roles LIMIT 1")).fetchall()
        assert filas is not None
    finally:
        db.close()
    rtt_ms = (time.perf_counter() - inicio) * 1000
    print(f"[INTEGRACION] Handshake Supabase RTT: {rtt_ms:.0f} ms")
    assert rtt_ms < 5000


def test_smtp_delivery_task():
    """El endpoint forgot-password encola correo sin bloquear al cliente."""
    with patch("src.api.routes.auth.email_service.enviar_pin_recuperacion") as mock_mail:
        inicio = time.perf_counter()
        response = client.post(
            "/auth/forgot-password",
            json={"email": "admin@pnp.gob.pe"},
        )
        elapsed = time.perf_counter() - inicio
    assert response.status_code == 200
    assert response.json().get("success") is True
    assert elapsed < 5.0
    print(f"[INTEGRACION] Respuesta forgot-password en {elapsed:.2f}s (SMTP en BackgroundTasks)")
