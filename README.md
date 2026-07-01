# integrador_gnn — Backend

API predictiva delictiva (FastAPI + GNN + JWT + PostGIS).

## Inicio rápido (equipo / laboratorio)

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt          # Python 3.10–3.12
# pip install -r requirements-local.txt  # Python 3.13+

cp .env.example .env
# Editar DATABASE_URL y SECRET_KEY

python scripts/check_artifacts.py      # Verifica archivos ML
python scripts/apply_migrations.py     # Migraciones APF3 (001–003)
python src/utils/create_admin.py       # Admin por defecto
python scripts/seed_e2e.py             # Usuarios y denuncia de prueba
uvicorn src.api.main:app --reload --port 8000
```

Frontend Selenium: `http://localhost:3000` · API: `http://localhost:8000`

---

## Modo prueba (`TEST_MODE`) — solo laboratorio

Para pruebas Selenium en el colegio **sin depender de Gmail** y **sin bloqueos por rate limit**:

```env
TEST_MODE=1
TEST_PIN=123456
```

| Con `TEST_MODE=1` | Efecto |
|-------------------|--------|
| Rate limit | Desactivado (login, forgot, verify, denuncias) |
| Recuperación de clave | PIN fijo (`TEST_PIN`) impreso en consola del servidor |
| SMTP | No se envía correo real |

**No activar en producción ni en despliegue público.**

Sin `TEST_MODE`, si `EMAIL_USER=tu_correo@gmail.com`, el PIN se simula solo en logs.

---

## Usuarios de prueba

| Email | Contraseña | Rol (`id_rol`) | Uso |
|-------|------------|----------------|-----|
| `admin@pnp.gob.pe` | `TesisUTP2026*` | 1 Administrador | Login, dashboard, admin |
| `analista@pnp.gob.pe` | `clave123` | 2 Analista | Inbox, denuncias |
| `investigador@pnp.gob.pe` | `clave123` | 3 Investigador | Admin upload/retrain |

Creados con `create_admin.py` y `scripts/seed_e2e.py` (idempotentes).

---

## Artefactos ML obligatorios

El servidor **no arranca** sin:

- `data/processed/grafo_edge_index.npz`
- `src/model/pesos_stgnn_pnp.pth`
- `src/model/tensor_panel.npy`

Opcional: `src/model/panel_dates.json`

```bash
python scripts/check_artifacts.py
```

Obtener los archivos del equipo (Drive/USB) si no están en el clone.

---

## Scripts útiles

| Script | Descripción |
|--------|-------------|
| `scripts/apply_migrations.py` | Aplica SQL en `migrations/` |
| `scripts/seed_e2e.py` | Usuarios E2E + 1 denuncia pendiente |
| `scripts/check_artifacts.py` | Comprueba artefactos ML |
| `src/utils/create_admin.py` | Crea `admin@pnp.gob.pe` |

---

## Cambios recientes (rama `matias`)

### Seguridad y pruebas
- **`TEST_MODE`** en `src/core/config.py` — modo laboratorio opt-in.
- **Rate limit** respeta `TEST_MODE`; alcances separados (login / forgot / verify / denuncia).
- **`forgot-password`**: ya no penaliza cada solicitud válida como fallo de rate limit.
- **PIN fijo** en modo prueba; log en consola y en `email_service`.

### Datos E2E
- **`scripts/seed_e2e.py`**: `analista@`, `investigador@`, denuncia pendiente para Inbox (test_05).

### Documentación
- **`.env.example`** ampliado (`TEST_MODE`, `TEST_PIN`, SMTP).

---

## Pruebas

```bash
pytest tests/test_security_robustness.py -v
pytest tests/test_denuncias.py -v
pytest tests/test_db_integration.py -v
```

---

## Integración frontend

- CORS: `http://localhost:5173`, `http://localhost:3000`
- `POST /auth/login` → JWT + `rol_id`
- Contrato E2E: ver `../CONTRATO_PRUEBAS_E2E.txt`

## Rama

`matias` → https://github.com/Josueav09/integrador_gnn.git
