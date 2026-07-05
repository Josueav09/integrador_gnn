#!/usr/bin/env python3
"""
Datos de prueba idempotentes para Selenium y laboratorio (APF3).
Ejecutar después de migraciones y create_admin.
"""
import sys
from datetime import date, time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from src.core.database import SessionLocal
from src.core.models import Usuario, DenunciaCiudadana
from src.repository.denuncia_repo import DenunciaRepository
from src.security.hashing import Hash

USUARIOS_E2E = [
    {
        "email": "analista@pnp.gob.pe",
        "nombre": "Analista",
        "apellido": "PNP",
        "password": "clave123",
        "id_rol": 2,
    },
    {
        "email": "investigador@pnp.gob.pe",
        "nombre": "Investigador",
        "apellido": "PNP",
        "password": "clave123",
        "id_rol": 3,
    },
]

DENUNCIA_E2E_DESC = "Reporte E2E de prueba — cuarentena pendiente (seed_e2e)."


def _crear_usuario(db, datos: dict) -> None:
    existe = db.query(Usuario).filter(Usuario.email_usuario_sistema == datos["email"]).first()
    if existe:
        print(f"[OK] Usuario ya existe: {datos['email']}")
        return

    db.add(
        Usuario(
            id_rol=datos["id_rol"],
            nombre_usuario_sistema=datos["nombre"],
            apellido_usuario_sistema=datos["apellido"],
            email_usuario_sistema=datos["email"],
            password_usuario_sistema=Hash.bcrypt(datos["password"]),
        )
    )
    db.commit()
    print(f"[CREADO] {datos['email']} | clave: {datos['password']} | rol: {datos['id_rol']}")


def _crear_denuncia_pendiente(db) -> None:
    pendientes = db.query(DenunciaCiudadana).filter(DenunciaCiudadana.estado == "pendiente").count()
    if pendientes > 0:
        print(f"[OK] Ya hay {pendientes} denuncia(s) pendiente(s); no se crea otra.")
        return

    repo = DenunciaRepository(db)
    denuncia = repo.create_denuncia_publica(
        id_tipo_delito=2,
        fecha_delito=date.today(),
        hora_delito=time(14, 30),
        lat=-12.0464,
        lng=-77.0428,
        descripcion=DENUNCIA_E2E_DESC,
    )
    print(f"[CREADO] Denuncia pendiente #{denuncia.id_denuncia_ciudadana} para Inbox (test_05).")


def main() -> None:
    print("=== SEED E2E (usuarios + denuncia pendiente) ===")
    db = SessionLocal()
    try:
        for usuario in USUARIOS_E2E:
            _crear_usuario(db, usuario)
        _crear_denuncia_pendiente(db)
        print("\nCredenciales documentadas:")
        print("  admin@pnp.gob.pe / TesisUTP2026* (rol 1)")
        print("  analista@pnp.gob.pe / clave123 (rol 2)")
        print("  investigador@pnp.gob.pe / clave123 (rol 3)")
    except Exception as exc:
        db.rollback()
        print(f"[ERROR] {exc}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
