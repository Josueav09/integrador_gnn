# integrador_gnn — Backend

API predictiva delictiva (FastAPI + GNN + JWT + PostGIS).

## Desarrollo local

**Python 3.10–3.12** (igual que Docker):

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Python 3.13+** (ej. 3.14 en Windows): usar `requirements-local.txt` porque `torch==2.5.1` no publica wheels para esa versión.

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-local.txt
```

Luego:

```bash
cp .env.example .env
# Configurar DATABASE_URL y ejecutar migraciones / seed según su entorno
python src/utils/create_admin.py
uvicorn src.api.main:app --reload --port 8000
```

Credenciales por defecto del admin: `admin@pnp.gob.pe` / `TesisUTP2026*`

## Integración con el frontend

- CORS habilitado para `http://localhost:5173`
- `POST /auth/login` → JWT
- `POST /predict/predecir?top_k=50` → hotspots (requiere Bearer token)

Regenerar datos históricos para el front:

```bash
python scripts/generate_front_historico.py
```

## Artefactos requeridos al arranque

- `data/processed/grafo_edge_index.npz`
- `src/model/pesos_stgnn_pnp.pth`
