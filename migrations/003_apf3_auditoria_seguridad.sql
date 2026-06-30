-- APF3 Migration 003: trazabilidad de eventos de seguridad
-- Tabla nueva: auditoria_seguridad
-- Evidencia para Anexo D (rate limiting, XSS/SQLi, fuerza bruta)

CREATE TABLE IF NOT EXISTS auditoria_seguridad (
    id_evento SERIAL PRIMARY KEY,
    tipo_evento VARCHAR(50) NOT NULL,
    ip_origen VARCHAR(45),
    email_usuario VARCHAR(150),
    detalle TEXT,
    nivel VARCHAR(20) NOT NULL DEFAULT 'INFO',
    fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_auditoria_seguridad_tipo
    ON auditoria_seguridad (tipo_evento);

CREATE INDEX IF NOT EXISTS idx_auditoria_seguridad_fecha
    ON auditoria_seguridad (fecha_creacion DESC);

COMMENT ON TABLE auditoria_seguridad IS 'Registro persistente de bloqueos IP, PIN y mitigaciones OWASP';
