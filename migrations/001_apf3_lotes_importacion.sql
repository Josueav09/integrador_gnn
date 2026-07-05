-- APF3 Migration 001: columnas de validación en lotes de importación
-- Tabla afectada: lotes_importacion
-- Compatible con carga CSV/JSON del admin y reportes Selenium test_06_admin_retrain

ALTER TABLE lotes_importacion
    ADD COLUMN IF NOT EXISTS validos INTEGER NOT NULL DEFAULT 0;

ALTER TABLE lotes_importacion
    ADD COLUMN IF NOT EXISTS invalidos INTEGER NOT NULL DEFAULT 0;

COMMENT ON COLUMN lotes_importacion.validos IS 'Registros que pasaron validación de esquema APF3';
COMMENT ON COLUMN lotes_importacion.invalidos IS 'Registros rechazados por esquema inválido';
