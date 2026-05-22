import csv
import sys
from pathlib import Path
from collections import deque

# Engaño arquitectónico para evitar el ModuleNotFoundError
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from sqlalchemy.orm import Session
from sqlalchemy import text
from src.core.database import SessionLocal 

CSV_PATH = BASE_DIR / "data" / "processed" / "dataset_gnn_granular_final.csv"

def poblar_historico_db():
    print("Iniciando ETL: Limpiando BD y extrayendo los ÚLTIMOS 5000 registros...")
    db: Session = SessionLocal()
    
    try:
        # 0. Limpieza (Idempotencia del ETL): Borramos los delitos viejos
        db.execute(text("TRUNCATE TABLE delitos CASCADE;"))
        db.commit()
        print("Tabla 'delitos' limpiada con éxito.")

        # 1. Asegurar Tipos de Delitos
        db.execute(text("""
            INSERT INTO tipos_delitos (id_tipo_delito, codigo_tipo_delito, nombre_tipo_delito, categoria_tipo_delito) 
            VALUES 
            (1, 'ROB-001', 'Robo agravado', 'Contra el Patrimonio'),
            (2, 'HUR-001', 'Hurto simple', 'Contra el Patrimonio')
            ON CONFLICT (codigo_tipo_delito) DO NOTHING;
        """))
        
        # 2. Asegurar Topología (Distrito y Cuadrante Maestro)
        # db.execute(text("""
        #     INSERT INTO distritos (id_distrito, nombre_distrito, codigo_ubigeo_distrito) 
        #     VALUES (1, 'Lima Centro', '150101')
        #     ON CONFLICT (codigo_ubigeo_distrito) DO NOTHING;
            
        #     INSERT INTO cuadrantes (id_cuadrante, id_distrito, codigo_cuadrante, nombre_cuadrante, centroide) 
        #     VALUES (1, 1, 'CUA-001', 'Cuadrante Maestro', ST_SetSRID(ST_MakePoint(-77.0428, -12.0464), 4326))
        #     ON CONFLICT (codigo_cuadrante) DO NOTHING;
        # """))
        db.commit()

        # 3. Lectura Eficiente de los ÚLTIMOS 5000 registros usando Deque
        ultimos_registros = deque(maxlen=5000)
        with open(CSV_PATH, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                ultimos_registros.append(row)
                
        print(f"CSV procesado. Se retuvieron los {len(ultimos_registros)} registros más recientes.")

        # 4. Ingesta Masiva por Lotes
        lote_size = 1000
        valores_insert = []
        contador = 0
        
        for row in ultimos_registros:
            lat = float(row["latitud"])
            lng = float(row["longitud"])
            
            tipo_delito = row.get("tipo_delito", "").strip().upper()
            id_tipo = 2 if "HURTO" in tipo_delito else 1
            
            valores_insert.append({
                "id_cuadrante": 1,
                "id_tipo_delito": id_tipo,
                "fecha": row.get("fecha", "2024-05-20"), # Asegura la fecha
                "lng": lng,
                "lat": lat
            })
            contador += 1
            
            if len(valores_insert) >= lote_size:
                _insertar_lote(db, valores_insert)
                valores_insert = []
                print(f"Insertados {contador} registros recientes...")
                
        # Insertar remanente
        if valores_insert:
            _insertar_lote(db, valores_insert)
            
        print(f"ETL Completado. {contador} incidentes geoespaciales recientes cargados en PostGIS.")

    except Exception as e:
        db.rollback()
        print(f"Error crítico en ETL: {str(e)}")
    finally:
        db.close()

def _insertar_lote(db, valores):
    query = text("""
        INSERT INTO delitos (id_cuadrante, id_tipo_delito, fecha_delito, ubicacion_exacta)
        VALUES (:id_cuadrante, :id_tipo_delito, :fecha, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326))
    """)
    db.execute(query, valores)
    db.commit()

if __name__ == "__main__":
    poblar_historico_db()