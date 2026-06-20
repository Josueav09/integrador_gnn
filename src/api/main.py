import sys
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
import torch
import numpy as np

# 1. Rutas
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from src.model.st_gnn import RedEspacioTemporal

# --- IMPORTACIÓN DE LOS NUEVOS ROUTERS MODULARES ---
from src.api.routes import auth, predict, dashboard, denuncias, usuarios, admin, monitoring
# ---------------------------------------------------

ml_models = {}
hardware_device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
UMBRAL_PNP = 0.0007 

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"\n=== INICIANDO SERVIDOR DE INTELIGENCIA PNP ===")
    
    try:
        ruta_grafo = BASE_DIR / "data" / "processed" / "grafo_edge_index.npz"
        grafo_data = np.load(ruta_grafo)
        
        ml_models["edge_index"] = torch.tensor(grafo_data['edge_index'], dtype=torch.long).to(hardware_device)
        ml_models["edge_weights"] = torch.tensor(grafo_data['edge_weights'], dtype=torch.float32).to(hardware_device)
        
        modelo = RedEspacioTemporal(num_features=5, unidades_ocultas=64).to(hardware_device)
        ruta_pesos = BASE_DIR / "src" / "model" / "pesos_stgnn_pnp.pth"
        
        modelo.load_state_dict(torch.load(ruta_pesos, map_location=hardware_device, weights_only=True))
        modelo.eval()
        ml_models["gnn"] = modelo

        print("¡Sistema Predictivo Operativo, Seguro y en Línea!")
        
    except Exception as e:
        print(f"[ERROR CRÍTICO AL ARRANCAR SERVIDOR]: {str(e)}")
        raise e
        
    yield
    ml_models.clear()

from fastapi.middleware.cors import CORSMiddleware

# 2. Inicialización de FastAPI
app = FastAPI(
    title="API - Sistema Predictivo Delictivo PNP",
    description="Motor de Inferencia Espaciotemporal con GNN protegido con JWT",
    version="2.0.0",
    lifespan=lifespan
)

# --- CONFIGURACIÓN DE CORS PARA EL FRONTEND ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"], # En prod cambiar "*" por los dominios reales
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MIDDLEWARE DE CABECERAS DE SEGURIDAD RECOMENDADAS POR OWASP ---
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

# 3. REGISTRO DE MÓDULOS EN EL MONOLITO
app.include_router(auth.router)
app.include_router(predict.router)
app.include_router(dashboard.router)
app.include_router(denuncias.router)
app.include_router(usuarios.router)
app.include_router(admin.router)
app.include_router(monitoring.router)

@app.get("/")
async def health_check():
    return {"status": "ok", "message": "API Predictiva GNN funcionando con Arquitectura Modular"}