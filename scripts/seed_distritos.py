import pandas as pd
import sys
from pathlib import Path
from sqlalchemy import text

# --- Corrección de rutas para encontrar 'src' ---
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from src.core.database import SessionLocal

def poblar_distritos():
    print("Iniciando carga de Distritos...")
    db = SessionLocal()
    
    try:
        # Cargamos el CSV desde la ruta correcta
        csv_path = BASE_DIR / "data" / "processed" / "dataset_gnn_granular_final.csv"
        df = pd.read_csv(csv_path)
        
        # Limpieza: Eliminamos espacios, convertimos a mayúsculas y quitamos nulos
        distritos_unicos = df['distrito'].dropna().str.strip().str.upper().unique()
        
        print(f"Detectados {len(distritos_unicos)} distritos únicos.")
        
        # Inserción
        for nombre in distritos_unicos:
            # ELIMINAMOS el id_distrito de la inserción y dejamos que Postgres use el SERIAL
            query = text("""
                INSERT INTO distritos (nombre_distrito, codigo_ubigeo_distrito, provincia_distrito)
                VALUES (:nombre, :codigo, 'Lima')
                ON CONFLICT (codigo_ubigeo_distrito) DO NOTHING;
            """)
            db.execute(query, {"nombre": nombre, "codigo": nombre[:5]}) 
            
        db.commit()
        print("Tabla 'distritos' poblada correctamente.")
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    poblar_distritos()