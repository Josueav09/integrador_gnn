-- APF3 Migration 002: bandeja de cuarentena (crowdsourcing)
-- Tabla afectada: denuncias_ciudadanas
-- Flujos: test_01_public_crime_report, test_05_quarantine_inbox

CREATE TABLE IF NOT EXISTS denuncias_ciudadanas (
    id_denuncia_ciudadana SERIAL PRIMARY KEY,
    id_tipo_delito INTEGER NOT NULL REFERENCES tipos_delitos(id_tipo_delito) ON DELETE RESTRICT,
    fecha_delito DATE NOT NULL,
    hora_delito TIME,
    ubicacion_exacta GEOMETRY(POINT, 4326) NOT NULL,
    descripcion TEXT,
    estado VARCHAR(20) NOT NULL DEFAULT 'pendiente',
    fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_denuncias_ciudadanas_estado
    ON denuncias_ciudadanas (estado);

CREATE INDEX IF NOT EXISTS idx_denuncias_ciudadanas_fecha
    ON denuncias_ciudadanas (fecha_creacion DESC);

COMMENT ON TABLE denuncias_ciudadanas IS 'Cola de cuarentena para denuncias ciudadanas antes de ST_Contains/PostGIS';
