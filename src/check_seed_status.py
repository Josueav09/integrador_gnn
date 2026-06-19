from sqlalchemy import text
from src.core.database import SessionLocal

db = SessionLocal()
try:
    print("Distritos:", db.execute(text("SELECT COUNT(*) FROM distritos")).scalar())
    print("Cuadrantes:", db.execute(text("SELECT COUNT(*) FROM cuadrantes")).scalar())
    print("Adyacencias:", db.execute(text("SELECT COUNT(*) FROM cuadrantes_adyacentes")).scalar())
    print("Delitos:", db.execute(text("SELECT COUNT(*) FROM delitos")).scalar())
    print("Modelos:", db.execute(text("SELECT COUNT(*) FROM modelos_gnn")).scalar())
except Exception as e:
    print("Error:", e)
finally:
    db.close()
