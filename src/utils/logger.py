import logging
import sys
from pathlib import Path

# 1. Crear carpeta de logs en la raíz si no existe
LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# 2. Configurar el diseño formal de la traza (Fecha | Nivel de Alerta | Mensaje)
log_format = logging.Formatter(
    fmt="%(asctime)s | [%(levelname)s] | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# 3. Handler para archivo físico (Persistencia para auditorías externas)
file_handler = logging.FileHandler(LOG_DIR / "auditoria_pnp.log", encoding="utf-8")
file_handler.setFormatter(log_format)

# 4. Handler para consola (Muestra la traza en la terminal de Docker)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_format)

# 5. Inicializar el Logger Oficial del Ecosistema
logger = logging.getLogger("PNP_Predictivo")
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)