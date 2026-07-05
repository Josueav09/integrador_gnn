# Migraciones SQL APF3

Ejecutar en Supabase/PostgreSQL **antes** de desplegar o correr pruebas Selenium de integración:

```bash
cd integrador_gnn
python scripts/apply_migrations.py
```

## Archivos

| Archivo | Tablas afectadas | Propósito |
|---------|------------------|-----------|
| `001_apf3_lotes_importacion.sql` | `lotes_importacion` | Columnas `validos`, `invalidos` para carga CSV admin |
| `002_apf3_denuncias_cuarentena.sql` | `denuncias_ciudadanas` | Cola de cuarentena + índices (test_01, test_05) |
| `003_apf3_auditoria_seguridad.sql` | `auditoria_seguridad` (nueva) | Trazabilidad de eventos de seguridad APF3 |

Todas las migraciones son **aditivas** (`IF NOT EXISTS`) y no eliminan datos existentes.
