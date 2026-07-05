#!/usr/bin/env python3
"""Verifica que existan los artefactos ML necesarios para arrancar la API."""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

REQUIRED = [
    BASE_DIR / "data" / "processed" / "grafo_edge_index.npz",
    BASE_DIR / "src" / "model" / "pesos_stgnn_pnp.pth",
    BASE_DIR / "src" / "model" / "tensor_panel.npy",
]

OPTIONAL = [
    BASE_DIR / "src" / "model" / "panel_dates.json",
]


def main() -> int:
    missing = [p for p in REQUIRED if not p.exists()]
    print("=== Verificación de artefactos ML ===\n")
    for path in REQUIRED + OPTIONAL:
        label = "OK" if path.exists() else ("FALTA" if path in missing else "opcional — ausente")
        print(f"  [{label:8}] {path.relative_to(BASE_DIR)}")

    if missing:
        print("\nFaltan archivos obligatorios. Obténlos del equipo (Drive/USB) antes de uvicorn.")
        return 1

    print("\nTodos los artefactos obligatorios están presentes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
