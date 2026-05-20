import sys
from pathlib import Path

# Configurar ruta para que Python encuentre la carpeta 'src'
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from src.core.database import SessionLocal
from sqlalchemy import text

print("=== INICIANDO PRUEBA DE CONEXIÓN A SUPABASE ===")

def probar_conexion():
    try:
        print("1. Intentando abrir sesión con la base de datos...")
        db = SessionLocal()
        
        print("2. Ejecutando consulta de prueba (Ping)...")
        # Hacemos una consulta SQL cruda para verificar que hay comunicación
        resultado = db.execute(text("SELECT id_rol, nombre_rol FROM sistema_roles")).fetchall()
        
        print("\n=== ¡CONEXIÓN EXITOSA! ===")
        print("Roles encontrados en Supabase:")
        for fila in resultado:
            print(f" - ID: {fila.id_rol} | Rol: {fila.nombre_rol}")
            
    except Exception as e:
        print("\n[ERROR FATAL] No se pudo conectar a la base de datos.")
        print(f"Detalle del error: {str(e)}")
    finally:
        # Siempre debemos cerrar la conexión
        if 'db' in locals():
            db.close()
            print("\n3. Sesión cerrada correctamente.")

if __name__ == "__main__":
    probar_conexion()