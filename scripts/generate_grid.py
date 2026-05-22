import sys
from pathlib import Path
import numpy as np
from sqlalchemy import text
from sqlalchemy.orm import Session

# Corrección de rutas para asegurar que 'src' esté en el path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from src.core.database import SessionLocal

def generar_grilla():
    print("Generando 400 nodos para la GNN...")
    db: Session = SessionLocal()
    
    # Coordenadas aproximadas de Lima Metropolitana
    min_lon, min_lat = -77.20, -12.30
    max_lon, max_lat = -76.80, -11.80
    
    # Queremos 400 nodos (20x20)
    n = 20
    lats = np.linspace(min_lat, max_lat, n)
    lons = np.linspace(min_lon, max_lon, n)
    
    try:
        # 1. Limpiamos la tabla para no tener conflictos
        # Usamos commit() para asegurar que la transacción se aplique
        db.execute(text("TRUNCATE TABLE cuadrantes CASCADE;"))
        db.commit()
        
        # 2. Insertar 400 nodos
        idx = 1
        for lat in lats:
            for lon in lons:
                query = text("""
                    INSERT INTO cuadrantes (id_cuadrante, id_distrito, codigo_cuadrante, nombre_cuadrante, centroide)
                    VALUES (:id, 1, :code, :name, ST_SetSRID(ST_MakePoint(:lon, :lat), 4326))
                """)
                
                # IMPORTANTE: Convertimos numpy types a float nativo de Python
                db.execute(query, {
                    "id": int(idx),
                    "code": f"CUA-{idx:03d}",
                    "name": f"Cuadrante {idx}",
                    "lon": float(lon), 
                    "lat": float(lat)
                })
                idx += 1
        
        db.commit()
        print(f"Éxito: 400 cuadrantes insertados en PostGIS.")
        
    except Exception as e:
        db.rollback()
        print(f"Error durante la inserción: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    generar_grilla()