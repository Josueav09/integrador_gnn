import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. Cargar las variables ocultas del archivo .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# 2. Configurar el Motor (Engine) de SQLAlchemy
# pool_pre_ping=True es vital para Supabase: verifica que la conexión no se 
# haya dormido antes de hacer una consulta, evitando errores en producción.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# 3. Fabrica de Sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Clase Base de la que heredarán todas nuestras tablas
Base = declarative_base()

def get_db():
    """
    Generador de base de datos. Se usará como Inyección de Dependencias 
    en nuestros endpoints de FastAPI para abrir y cerrar conexiones de forma segura.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()