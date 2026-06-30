"""
Aplica migraciones SQL en orden desde integrador_gnn/migrations/.
Uso:
  python scripts/apply_migrations.py
Requiere DATABASE_URL en .env o entorno.
"""
from __future__ import annotations

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from sqlalchemy import text

from src.core.database import engine


def main() -> None:
    migrations_dir = BASE_DIR / "migrations"
    files = sorted(migrations_dir.glob("*.sql"))
    if not files:
        print("No hay archivos .sql en migrations/")
        return

    print(f"=== Aplicando {len(files)} migración(es) APF3 ===")
    with engine.begin() as conn:
        for path in files:
            sql = path.read_text(encoding="utf-8")
            print(f"-> {path.name}")
            conn.execute(text(sql))
    print("=== Migraciones completadas ===")


if __name__ == "__main__":
    main()
