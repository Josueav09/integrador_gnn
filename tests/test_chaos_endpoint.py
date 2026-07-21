import sys
from pathlib import Path

from fastapi.testclient import TestClient

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

from src.api.main import app
from src.core.config import settings

client = TestClient(app)


def test_chaos_endpoint_bloqueado_fuera_de_laboratorio(monkeypatch):
    monkeypatch.setattr(settings, "TEST_MODE", False)

    response = client.post("/admin/chaos/crash")

    assert response.status_code == 403
    assert "laboratorio" in response.json()["detail"].lower()


def test_chaos_endpoint_simulacion_controlada_en_laboratorio(monkeypatch):
    monkeypatch.setattr(settings, "TEST_MODE", True)

    response = client.post("/admin/chaos/crash")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "simulado"
    assert payload["modo"] == "TEST_MODE"