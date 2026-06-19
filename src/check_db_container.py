import os
import sys
from sqlalchemy import text

# Import project's SessionLocal to avoid hardcoding database URLs
from src.core.database import SessionLocal

print("Connecting to database inside container using SessionLocal...")
db = SessionLocal()
try:
    tables = [
        "sistema_roles", "sistema_usuarios", "distritos", 
        "cuadrantes", "cuadrantes_adyacentes", "tipos_delitos", 
        "lotes_importacion", "delitos", "modelos_gnn", 
        "predicciones", "predicciones_cuadrantes"
    ]
    for t in tables:
        try:
            cnt = db.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
            print(f"Table '{t}': {cnt} records")
        except Exception as e:
            print(f"Table '{t}': Error: {e}")

    print("\n--- Modelos GNN ---")
    try:
        modelos = db.execute(text("SELECT id_modelo_gnn, version_modelo_gnn, nombre_modelo_gnn, f1_score_modelo_gnn, rmse_modelo_gnn, estado_modelo_gnn FROM modelos_gnn")).all()
        for m in modelos:
            print(f"ID: {m[0]} | Version: {m[1]} | Nombre: {m[2]} | F1: {m[3]} | RMSE: {m[4]} | Estado: {m[5]}")
    except Exception as e:
        print("Error reading modelos_gnn:", e)

    print("\n--- Sample Cuadrantes ---")
    try:
        cuadrantes = db.execute(text("SELECT id_cuadrante, codigo_cuadrante, id_distrito FROM cuadrantes LIMIT 5")).all()
        for c in cuadrantes:
            print(f"ID: {c[0]} | Codigo: {c[1]} | Distrito: {c[2]}")
    except Exception as e:
        print("Error reading cuadrantes:", e)

finally:
    db.close()
