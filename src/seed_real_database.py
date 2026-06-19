import os
import sys
import json
import csv
import numpy as np
from datetime import datetime, date, time
from sqlalchemy import text

# Import database connection
from src.core.database import SessionLocal

def seed_real_data():
    print("=== INICIANDO SEMILLADO ULTRA-OPTIMIZADO CON DATOS REALES DE GNN ===")
    db = SessionLocal()
    
    try:
        # 1. Obtener usuario administrador para relacionarlo
        admin_id = db.execute(text("SELECT id_usuario_sistema FROM sistema_usuarios WHERE email_usuario_sistema = 'admin@pnp.gob.pe'")).scalar()
        if not admin_id:
            # Si no existe admin, buscar cualquier usuario
            admin_id = db.execute(text("SELECT id_usuario_sistema FROM sistema_usuarios LIMIT 1")).scalar()
            if not admin_id:
                print("[ERROR] Debe crear al menos un usuario en sistema_usuarios para semillar.")
                return

        # 2. Limpiar tablas en cascada para evitar conflictos
        print("1. Limpiando tablas antiguas...")
        db.execute(text("TRUNCATE TABLE delitos, predicciones_cuadrantes, predicciones, cuadrantes_adyacentes, cuadrantes, lotes_importacion, modelos_gnn CASCADE;"))
        db.commit()
        print("   -> Tablas truncadas exitosamente.")

        # 3. Asegurar distritos
        node_csv_path = "src/model/node_mapping_summary.csv"
        distritos_reales = set()
        nodes_data = []
        
        with open(node_csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                distritos_reales.add(row['distrito'].strip().upper())
                nodes_data.append(row)

        print(f"2. Verificando {len(distritos_reales)} distritos en base de datos...")
        distritos_db = db.execute(text("SELECT id_distrito, nombre_distrito FROM distritos")).all()
        distrito_map = {d[1].strip().upper(): d[0] for d in distritos_db}

        # Insertar distritos faltantes
        for dname in distritos_reales:
            if dname not in distrito_map:
                query = text("""
                    INSERT INTO distritos (nombre_distrito, codigo_ubigeo_distrito, provincia_distrito)
                    VALUES (:nombre, :codigo, 'Lima')
                    RETURNING id_distrito;
                """)
                ubigeo = f"UB-{hash(dname) % 90000 + 10000}"
                new_id = db.execute(query, {"nombre": dname, "codigo": ubigeo}).scalar()
                distrito_map[dname] = new_id
                print(f"   -> Insertado distrito faltante: {dname}")
        db.commit()

        # 4. Insertar cuadrantes en lote
        print("3. Insertando 400 cuadrantes reales...")
        cuadrantes_values = []
        for row in nodes_data:
            id_nodo = int(row['id_nodo'])
            id_cuadrante = id_nodo + 1  # 1-indexed para base de datos
            dname = row['distrito'].strip().upper()
            id_distrito = distrito_map[dname]
            lat = float(row['lat_mean'])
            lon = float(row['lon_mean'])
            
            dname_escaped = row['distrito'].replace("'", "''").title()
            val = f"({id_cuadrante}, {id_distrito}, 'CUA-{id_cuadrante:03d}', 'Cuadrante {id_cuadrante} - {dname_escaped}', ST_SetSRID(ST_MakePoint({lon}, {lat}), 4326))"
            cuadrantes_values.append(val)
            
        query_cuadrantes_str = f"""
            INSERT INTO cuadrantes (id_cuadrante, id_distrito, codigo_cuadrante, nombre_cuadrante, centroide)
            VALUES {", ".join(cuadrantes_values)};
        """
        db.execute(text(query_cuadrantes_str))
        db.commit()
        print("   -> 400 cuadrantes reales insertados.")

        # 5. Insertar cuadrantes_adyacentes en lote (multi-row INSERT)
        print("4. Cargando topología real del grafo (2000 conexiones)...")
        grafo_path = "data/processed/grafo_edge_index.npz"
        if not os.path.exists(grafo_path):
            grafo_path = "/app/data/processed/grafo_edge_index.npz"
            
        grafo_data = np.load(grafo_path)
        edge_index = grafo_data['edge_index']
        edge_weights = grafo_data['edge_weights']
        
        ady_values = []
        for i in range(edge_index.shape[1]):
            u = int(edge_index[0, i]) + 1
            v = int(edge_index[1, i]) + 1
            w = min(float(edge_weights[i]), 99.9999)
            val = f"({u}, {v}, {w}, 'contiguo')"
            ady_values.append(val)
            
        query_ady_str = f"""
            INSERT INTO cuadrantes_adyacentes (id_cuadrante_origen, id_cuadrante_destino, peso_adyacencia, tipo_adyacencia)
            VALUES {", ".join(ady_values)}
            ON CONFLICT (id_cuadrante_origen, id_cuadrante_destino) DO NOTHING;
        """
        db.execute(text(query_ady_str))
        db.commit()
        print(f"   -> {len(ady_values)} conexiones del grafo insertadas.")

        # 6. Crear un Lote de Importación para los delitos reales (formato_lote debe ser 'csv' o 'json')
        print("5. Creando lote de importación para delitos...")
        query_lote = text("""
            INSERT INTO lotes_importacion (id_usuario_sistema, nombre_archivo_lote, formato_lote, total_registros, validos, invalidos, estado_lote)
            VALUES (:admin_id, 'dataset_features_gnn.csv', 'csv', 10000, 10000, 0, 'completado')
            RETURNING id_lote_importacion;
        """)
        id_lote = db.execute(query_lote, {"admin_id": admin_id}).scalar()
        db.commit()

        # 7. Insertar delitos reales en lote (multi-row INSERT)
        print("6. Insertando 10,000 delitos históricos reales...")
        crimes_json_path = "src/model/crimes_sample.json"
        with open(crimes_json_path, 'r', encoding='utf-8') as f:
            crimes = json.load(f)
            
        # Obtener los IDs de tipo de delito
        tipos_db = db.execute(text("SELECT id_tipo_delito, codigo_tipo_delito FROM tipos_delitos")).all()
        tipos_map = {t[1]: t[0] for t in tipos_db}

        if "ROB-001" not in tipos_map:
            db.execute(text("INSERT INTO tipos_delitos (id_tipo_delito, codigo_tipo_delito, nombre_tipo_delito, categoria_tipo_delito) VALUES (1, 'ROB-001', 'Robo Agravado', 'Patrimonio')"))
            tipos_map["ROB-001"] = 1
        if "HUR-001" not in tipos_map:
            db.execute(text("INSERT INTO tipos_delitos (id_tipo_delito, codigo_tipo_delito, nombre_tipo_delito, categoria_tipo_delito) VALUES (2, 'HUR-001', 'Hurto Simple', 'Patrimonio')"))
            tipos_map["HUR-001"] = 2
        db.commit()

        delito_values = []
        for c in crimes:
            id_cuadrante = int(c["id_nodo"]) + 1
            id_tipo = tipos_map.get(c["tipo_delito"], 1)
            
            desc_escaped = c["descripcion"].replace("'", "''")
            f_date = c["fecha_delito"]
            h_time = c["hora_delito"]
            lon = float(c["lng"])
            lat = float(c["lat"])
            
            val = f"({id_cuadrante}, {id_tipo}, {id_lote}, '{f_date}', '{h_time}', ST_SetSRID(ST_MakePoint({lon}, {lat}), 4326), '{desc_escaped}')"
            delito_values.append(val)
            
        chunk_size = 2000
        for i in range(0, len(delito_values), chunk_size):
            chunk = delito_values[i : i + chunk_size]
            query_delito_str = f"""
                INSERT INTO delitos (id_cuadrante, id_tipo_delito, id_lote_importacion, fecha_delito, hora_delito, ubicacion_exacta, descripcion_delito)
                VALUES {", ".join(chunk)};
            """
            db.execute(text(query_delito_str))
            db.commit()
            print(f"   -> Insertados {i + len(chunk)} delitos...")
            
        print("   -> 10,000 delitos históricos reales insertados con éxito.")

        # 8. Insertar Modelo GNN real con métricas reales
        print("7. Insertando modelo GNN v1.2 con métricas reales...")
        query_modelo = text("""
            INSERT INTO modelos_gnn (id_usuario_sistema, version_modelo_gnn, nombre_modelo_gnn, arquitectura_modelo_gnn, hiperparametros_modelo_gnn, ruta_archivo_modelo_gnn, rmse_modelo_gnn, f1_score_modelo_gnn, estado_modelo_gnn)
            VALUES (:admin_id, 'v1.2', 'ST-GNN Lima Metropolitana', 'ST-GNN', :hiper, 'src/model/pesos_stgnn_pnp.pth', 0.0456, 0.71, 'desplegado')
        """)
        db.execute(query_modelo, {
            "admin_id": admin_id,
            "hiper": json.dumps({"learning_rate": 0.001, "epochs": 30, "batch_size": 32, "hidden_dim": 64})
        })
        db.commit()
        print("   -> Modelo GNN v1.2 insertado y marcado como desplegado.")
        print("\n=== ¡PROCESO DE SEMILLADO DE DATOS REALES COMPLETADO CON ÉXITO! ===")

    except Exception as e:
        db.rollback()
        print(f"\n[ERROR CRÍTICO DURANTE EL SEMILLADO]: {str(e)}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    seed_real_data()
