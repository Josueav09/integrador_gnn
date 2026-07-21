#!/usr/bin/env python3
"""Genera evidencia básica de alta disponibilidad y recuperación.

El script no modifica el sistema. Solo verifica disponibilidad de la API,
lee métricas desde el endpoint de monitoreo y comprueba la configuración
de producción para documentar la capacidad de reinicio/recuperación.
"""

from __future__ import annotations

import json
import os
import time
import urllib.request
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
OUTPUT_FILE = LOG_DIR / "ha_dr_evidence.txt"
ROOT_URL = os.environ.get("HA_ROOT_URL", "http://127.0.0.1:8000").rstrip("/")
MONITOR_URL = os.environ.get("HA_MONITOR_URL", f"{ROOT_URL}/monitoring/status")
COMPOSE_FILE = BASE_DIR / "docker-compose.prod.yml"


def fetch_json(url: str) -> tuple[float, dict]:
    start = time.perf_counter()
    with urllib.request.urlopen(url, timeout=10) as response:
        payload = json.loads(response.read().decode("utf-8"))
    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
    return elapsed_ms, payload


def main() -> int:
    lines: list[str] = []
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    lines.append(f"Fecha/Hora: {timestamp}")

    root_latency, root_payload = fetch_json(ROOT_URL)
    lines.append(f"ROOT_LATENCY_MS={root_latency}")
    lines.append(f"ROOT_STATUS={root_payload.get('status')}")

    monitor_latency, monitor_payload = fetch_json(MONITOR_URL)
    lines.append(f"MONITOR_LATENCY_MS={monitor_latency}")
    lines.append(f"MONITOR_STATUS={monitor_payload.get('status')}")
    lines.append(f"DB_STATE={monitor_payload.get('base_de_datos', {}).get('estado')}")
    lines.append(f"DB_LATENCY_MS={monitor_payload.get('base_de_datos', {}).get('latencia_ms')}")
    lines.append(f"GNN_STATE={monitor_payload.get('modelo_gnn', {}).get('estado')}")
    lines.append(f"CPU={monitor_payload.get('recursos_servidor', {}).get('cpu_uso_porcentaje')}")
    lines.append(f"MEMORY_MB={monitor_payload.get('recursos_servidor', {}).get('memoria_rss_mb')}")

    compose_text = COMPOSE_FILE.read_text(encoding="utf-8")
    lines.append(f"PROD_RESTART_POLICY={'restart: unless-stopped' in compose_text}")
    lines.append(f"PROD_TEST_MODE_ZERO={'TEST_MODE: \"0\"' in compose_text}")

    OUTPUT_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("=== Evidencia HA/DR generada ===")
    print(OUTPUT_FILE)
    for line in lines:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())