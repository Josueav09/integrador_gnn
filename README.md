# integrador_gnn — Backend

API predictiva delictiva (FastAPI + GNN + JWT + PostGIS).

## Desarrollo local

```bash
pip install -r requirements.txt
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
