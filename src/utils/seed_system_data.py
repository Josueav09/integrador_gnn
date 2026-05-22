import os
import sys
import random
from datetime import datetime, date, time, timedelta
from pathlib import Path

# Configurar rutas para importar desde src
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from src.core.database import SessionLocal
from src.core.models import (
    Usuario, Distrito, Cuadrante, TipoDelito, 
    Delito, ModeloGNN, Prediccion, PrediccionCuadrante,
    CuadranteAdyacente
)
from sqlalchemy import text

def seed_database():
    print("=== INICIANDO SEMILLADO DE BASE DE DATOS PNP ===")
    db = SessionLocal()
    
    try:
        # 1. Obtener usuario administrador o investigador
        admin = db.query(Usuario).filter(Usuario.email_usuario_sistema == "admin@pnp.gob.pe").first()
        if not admin:
            print("[ERROR] Debe ejecutar create_admin.py primero para tener el usuario 'admin@pnp.gob.pe'")
            return
            
        # 2. Tipos de Delito
        print("2. Verificando tipos de delitos...")
        tipos = [
            {"id_tipo_delito": 1, "codigo_tipo_delito": "ROB-001", "nombre_tipo_delito": "Robo Agravado", "categoria_tipo_delito": "Patrimonio", "descripcion_tipo_delito": "Robo con violencia o amenaza"},
            {"id_tipo_delito": 2, "codigo_tipo_delito": "HUR-001", "nombre_tipo_delito": "Hurto Simple", "categoria_tipo_delito": "Patrimonio", "descripcion_tipo_delito": "Sustracción sin violencia"},
            {"id_tipo_delito": 3, "codigo_tipo_delito": "VAND-001", "nombre_tipo_delito": "Vandalismo y Daños", "categoria_tipo_delito": "Seguridad Pública", "descripcion_tipo_delito": "Daño a propiedad pública o privada"},
            {"id_tipo_delito": 4, "codigo_tipo_delito": "FRAU-001", "nombre_tipo_delito": "Fraude o Estafa", "categoria_tipo_delito": "Patrimonio", "descripcion_tipo_delito": "Engaño económico"}
        ]
        
        for t in tipos:
            existe = db.query(TipoDelito).filter(TipoDelito.codigo_tipo_delito == t["codigo_tipo_delito"]).first()
            if not existe:
                nuevo_tipo = TipoDelito(**t)
                db.add(nuevo_tipo)
                print(f"   -> Insertado: {t['nombre_tipo_delito']}")
        db.commit()

        # 3. Lotes de Importación (Historial de cargas)
        print("3. Verificando historial de cargas...")
        total_lotes = db.execute(text("SELECT COUNT(*) FROM lotes_importacion")).scalar() or 0
        if total_lotes == 0:
            query_lote = text("""
                INSERT INTO lotes_importacion (id_usuario_sistema, nombre_archivo_lote, formato_lote, total_registros, validos, invalidos, estado_lote, fecha_creacion)
                VALUES (:id_user, :filename, :format, :total, :valid, :invalid, :state, :fecha)
            """)
            db.execute(query_lote, {
                "id_user": admin.id_usuario_sistema,
                "filename": "delitos_mayo_2026.csv",
                "format": "csv",
                "total": 15420,
                "valid": 15420,
                "invalid": 0,
                "state": "completado",
                "fecha": datetime.now() - timedelta(days=2)
            })
            db.execute(query_lote, {
                "id_user": admin.id_usuario_sistema,
                "filename": "delitos_abril_2026.json",
                "format": "json",
                "total": 14230,
                "valid": 14230,
                "invalid": 0,
                "state": "completado",
                "fecha": datetime.now() - timedelta(days=32)
            })
            db.commit()
            print("   -> Insertados 2 lotes de importación de prueba.")

        # 4. Adyacencias de Cuadrantes (Si no hay)
        print("4. Generando adyacencias de cuadrantes (Grafo de 400 nodos)...")
        adyacencias_count = db.query(CuadranteAdyacente).count()
        if adyacencias_count == 0:
            # Grilla de 20x20
            cuadrantes = db.query(Cuadrante).order_by(Cuadrante.id_cuadrante).all()
            if len(cuadrantes) == 400:
                print("   -> Detectados 400 cuadrantes en BD. Construyendo adyacencias de grilla...")
                ady_list = []
                grid = [[cuadrantes[r * 20 + c].id_cuadrante for c in range(20)] for r in range(20)]
                
                for r in range(20):
                    for c in range(20):
                        curr_id = grid[r][c]
                        # Derecha
                        if c + 1 < 20:
                            ady_list.append(CuadranteAdyacente(id_cuadrante_origen=curr_id, id_cuadrante_destino=grid[r][c+1], peso_adyacencia=1.0, tipo_adyacencia="contiguo"))
                        # Abajo
                        if r + 1 < 20:
                            ady_list.append(CuadranteAdyacente(id_cuadrante_origen=curr_id, id_cuadrante_destino=grid[r+1][c], peso_adyacencia=1.0, tipo_adyacencia="contiguo"))
                
                db.add_all(ady_list)
                db.commit()
                print(f"   -> Insertadas {len(ady_list)} adyacencias de cuadrantes.")
            else:
                print(f"   -> Advertencia: Hay {len(cuadrantes)} cuadrantes (no son 400). Se omitirá la autogeneración de adyacencias.")

        # 5. Generar Delitos Históricos (Últimos 6 meses)
        print("5. Generando delitos históricos en la base de datos...")
        delitos_count = db.query(Delito).count()
        if delitos_count == 0:
            cuadrantes = db.query(Cuadrante).all()
            tipo_ids = [t.id_tipo_delito for t in db.query(TipoDelito).all()]
            lotes_ids = [row.id_lote_importacion for row in db.execute(text("SELECT id_lote_importacion FROM lotes_importacion")).all()]
            
            if cuadrantes and tipo_ids:
                print(f"   -> Generando 1,500 delitos aleatorios para {len(cuadrantes)} cuadrantes...")
                delito_list = []
                start_date = date(2026, 1, 1)
                
                random.seed(1337)
                for _ in range(1500):
                    cuad = random.choice(cuadrantes)
                    t_id = random.choice(tipo_ids)
                    l_id = random.choice(lotes_ids) if lotes_ids else None
                    f_delito = start_date + timedelta(days=random.randint(0, 145))
                    h_delito = time(random.randint(0, 23), random.choice([0, 15, 30, 45]))
                    
                    delito_list.append(Delito(
                        id_cuadrante=cuad.id_cuadrante,
                        id_tipo_delito=t_id,
                        id_lote_importacion=l_id,
                        fecha_delito=f_delito,
                        hora_delito=h_delito,
                        ubicacion_exacta=cuad.centroide,
                        descripcion_delito=f"Incidente delictivo registrado en cuadrante {cuad.codigo_cuadrante}"
                    ))
                
                db.add_all(delito_list)
                db.commit()
                print("   -> ¡1,500 delitos históricos agregados con éxito!")
            else:
                print("   -> No hay cuadrantes o tipos de delito creados para semillar delitos.")

        # 6. Modelo GNN
        print("6. Verificando modelo GNN...")
        modelo = db.query(ModeloGNN).filter(ModeloGNN.version_modelo_gnn == "v1.2").first()
        if not modelo:
            modelo = ModeloGNN(
                id_usuario_sistema=admin.id_usuario_sistema,
                version_modelo_gnn="v1.2",
                nombre_modelo_gnn="ST-GNN Lima Metropolitana",
                arquitectura_modelo_gnn="ST-GNN",
                hiperparametros_modelo_gnn={"learning_rate": 0.001, "epochs": 150, "batch_size": 32, "hidden_dim": 64},
                ruta_archivo_modelo_gnn="models/model_v1.2.pt",
                rmse_modelo_gnn=12.7,
                f1_score_modelo_gnn=0.89,
                estado_modelo_gnn="desplegado"
            )
            db.add(modelo)
            db.commit()
            print("   -> Modelo GNN v1.2 insertado y marcado como desplegado.")
        else:
            modelo.estado_modelo_gnn = "desplegado"
            db.commit()
            print("   -> Modelo GNN v1.2 existente marcado como desplegado.")

        # 7. Predicciones y Predicciones Cuadrantes (Para fechas recientes)
        print("7. Generando predicciones GNN para todas las zonas...")
        target_dates = [date(2026, 5, 20), date(2026, 5, 22), date.today()]
        cuadrantes = db.query(Cuadrante).all()
        modelo = db.query(ModeloGNN).filter(ModeloGNN.version_modelo_gnn == "v1.2").first()
        
        for t_date in target_dates:
            pred_db = db.query(Prediccion).filter(
                Prediccion.fecha_objetivo_prediccion == t_date,
                Prediccion.id_modelo_gnn == modelo.id_modelo_gnn
            ).first()
            
            if not pred_db:
                print(f"   -> Creando predicciones para la fecha: {t_date}")
                pred_db = Prediccion(
                    id_modelo_gnn=modelo.id_modelo_gnn,
                    id_usuario_sistema=admin.id_usuario_sistema,
                    fecha_objetivo_prediccion=t_date,
                    latencia_ms_prediccion=145,
                    estado_prediccion="completado"
                )
                db.add(pred_db)
                db.commit() # Guardar para obtener id_prediccion
                
                vals = []
                for cuad in cuadrantes:
                    score = round(random.uniform(0.05, 0.95), 4)
                    level = "alto" if score > 0.7 else ("medio" if score > 0.3 else "bajo")
                    vals.append(PrediccionCuadrante(
                        id_prediccion=pred_db.id_prediccion,
                        id_cuadrante=cuad.id_cuadrante,
                        score_riesgo=score,
                        nivel_riesgo=level
                    ))
                db.add_all(vals)
                db.commit()
                print(f"   -> {len(vals)} cuadrantes mapeados con predicciones de riesgo.")

        print("\n=== ¡BASE DE DATOS TOTALMENTE SEMILLADA Y LISTA PARA OPERAR! ===")
        
    except Exception as e:
        print(f"[ERROR FATAL EN SEMILLERO]: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
