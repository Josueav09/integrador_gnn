import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")


def _env_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).lower() in ("1", "true", "yes", "on")


class Settings:
    PROJECT_TITLE: str = "API - Sistema Predictivo Delictivo PNP"
    PROJECT_VERSION: str = "2.0.0"

    DATABASE_URL: str = os.getenv("DATABASE_URL")

    SECRET_KEY: str = os.getenv("SECRET_KEY", "pnppredictivo_secreto_super_seguro_2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    UMBRAL_PNP: float = 0.0007

    EMAIL_USER: str = os.getenv("EMAIL_USER", "tu_correo@gmail.com")
    EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD", "tu_app_password")

    # Solo laboratorio / Selenium en colegio (nunca en producción)
    TEST_MODE: bool = _env_bool("TEST_MODE", False)
    TEST_PIN: str = os.getenv("TEST_PIN", "123456")


settings = Settings()
