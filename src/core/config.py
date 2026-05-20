import os
from dotenv import load_dotenv
from pathlib import Path

# Determinar la raíz del proyecto para ubicar el archivo .env
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings:
    PROJECT_TITLE: str = "API - Sistema Predictivo Delictivo PNP"
    PROJECT_VERSION: str = "2.0.0"
    
    # Base de Datos (Cargada desde el .env)
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    
    # Seguridad y Criptografía (Cargada desde el .env con fallback seguro)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "pnppredictivo_secreto_super_seguro_2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 horas (Turno policial estándar)
    
    # Parámetros del Negocio / Inteligencia Artificial
    UMBRAL_PNP: float = 0.0007

# Instancia única de configuración (Patrón Singleton)
settings = Settings()