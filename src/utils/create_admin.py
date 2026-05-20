import sys
from pathlib import Path

# Configurar rutas
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from src.core.database import SessionLocal
from src.core.models import Usuario
from src.security.hashing import Hash

def crear_administrador():
    print("=== INICIANDO CREACIÓN DE CREDENCIALES SECULARES ===")
    db = SessionLocal()
    try:
        # 1. Verificar si ya existe para no duplicarlo
        email_admin = "admin@pnp.gob.pe"
        existe = db.query(Usuario).filter(Usuario.email_usuario_sistema == email_admin).first()
        
        if existe:
            print(f"[Aviso] El usuario {email_admin} ya existe en la base de datos.")
            return

        # 2. Crear el objeto Usuario con contraseña encriptada
        nuevo_admin = Usuario(
            id_rol=1,  # El ID 1 corresponde a "Administrador" en tu tabla sistema_roles
            nombre_usuario_sistema="General",
            apellido_usuario_sistema="Director",
            email_usuario_sistema=email_admin,
            password_usuario_sistema=Hash.bcrypt("TesisUTP2026*") # <--- Contraseña protegida
        )
        
        # 3. Guardar en Supabase
        db.add(nuevo_admin)
        db.commit()
        print(f"[ÉXITO] ¡Administrador creado! Correo: {email_admin} | Clave: TesisUTP2026*")
        
    except Exception as e:
        print(f"[ERROR] Hubo un problema al crear el usuario: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    crear_administrador()