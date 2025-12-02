

-- Eliminar tablas si existen (para desarrollo)
DROP TABLE IF EXISTS aud_errores CASCADE;
DROP TABLE IF EXISTS aud_vehiculos CASCADE;
DROP TABLE IF EXISTS aud_ventas CASCADE;

-- Tabla de auditoría: Ventas

CREATE TABLE aud_ventas (
    id BIGSERIAL PRIMARY KEY,
    venta_id BIGINT,
    accion VARCHAR(10) NOT NULL,
    usuario_bd VARCHAR(100) NOT NULL,
    fecha_evento TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    old_data JSONB,
    new_data JSONB,
    CONSTRAINT chk_aud_ventas_accion CHECK (accion IN ('INSERT', 'UPDATE', 'DELETE'))
);

COMMENT ON TABLE aud_ventas IS 'Auditoría de cambios en la tabla venta';
COMMENT ON COLUMN aud_ventas.id IS 'Identificador único del registro de auditoría';
COMMENT ON COLUMN aud_ventas.venta_id IS 'ID de la venta afectada';
COMMENT ON COLUMN aud_ventas.accion IS 'Tipo de operación: INSERT, UPDATE, DELETE';
COMMENT ON COLUMN aud_ventas.usuario_bd IS 'Usuario de base de datos que realizó la operación';
COMMENT ON COLUMN aud_ventas.fecha_evento IS 'Fecha y hora del evento';
COMMENT ON COLUMN aud_ventas.old_data IS 'Datos anteriores (JSON) - NULL en INSERT';
COMMENT ON COLUMN aud_ventas.new_data IS 'Datos nuevos (JSON) - NULL en DELETE';

-- Índices para consultas de auditoría
CREATE INDEX idx_aud_ventas_venta_id ON aud_ventas(venta_id);
CREATE INDEX idx_aud_ventas_fecha ON aud_ventas(fecha_evento);
CREATE INDEX idx_aud_ventas_accion ON aud_ventas(accion);
CREATE INDEX idx_aud_ventas_usuario ON aud_ventas(usuario_bd);

-- Tabla de auditoría: Vehículos

CREATE TABLE aud_vehiculos (
    id BIGSERIAL PRIMARY KEY,
    vehiculo_id BIGINT,
    accion VARCHAR(10) NOT NULL,
    usuario_bd VARCHAR(100) NOT NULL,
    fecha_evento TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    old_data JSONB,
    new_data JSONB,
    CONSTRAINT chk_aud_vehiculos_accion CHECK (accion IN ('INSERT', 'UPDATE', 'DELETE'))
);

COMMENT ON TABLE aud_vehiculos IS 'Auditoría de cambios en la tabla vehiculo';
COMMENT ON COLUMN aud_vehiculos.id IS 'Identificador único del registro de auditoría';
COMMENT ON COLUMN aud_vehiculos.vehiculo_id IS 'ID del vehículo afectado';
COMMENT ON COLUMN aud_vehiculos.accion IS 'Tipo de operación: INSERT, UPDATE, DELETE';
COMMENT ON COLUMN aud_vehiculos.usuario_bd IS 'Usuario de base de datos que realizó la operación';
COMMENT ON COLUMN aud_vehiculos.fecha_evento IS 'Fecha y hora del evento';
COMMENT ON COLUMN aud_vehiculos.old_data IS 'Datos anteriores (JSON) - NULL en INSERT';
COMMENT ON COLUMN aud_vehiculos.new_data IS 'Datos nuevos (JSON) - NULL en DELETE';

-- Índices para consultas de auditoría
CREATE INDEX idx_aud_vehiculos_vehiculo_id ON aud_vehiculos(vehiculo_id);
CREATE INDEX idx_aud_vehiculos_fecha ON aud_vehiculos(fecha_evento);
CREATE INDEX idx_aud_vehiculos_accion ON aud_vehiculos(accion);
CREATE INDEX idx_aud_vehiculos_usuario ON aud_vehiculos(usuario_bd);

-- Tabla de auditoría: Errores

CREATE TABLE aud_errores (
    id BIGSERIAL PRIMARY KEY,
    origen VARCHAR(100) NOT NULL,
    detalle TEXT NOT NULL,
    sqlstate VARCHAR(10),
    sqlerrm TEXT,
    usuario_bd VARCHAR(100) NOT NULL,
    fecha_evento TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    contexto JSONB
);

COMMENT ON TABLE aud_errores IS 'Registro de errores capturados por bloques TRY/CATCH';
COMMENT ON COLUMN aud_errores.id IS 'Identificador único del error';
COMMENT ON COLUMN aud_errores.origen IS 'Nombre del procedimiento o función donde ocurrió el error';
COMMENT ON COLUMN aud_errores.detalle IS 'Descripción del error';
COMMENT ON COLUMN aud_errores.sqlstate IS 'Código de estado SQL del error';
COMMENT ON COLUMN aud_errores.sqlerrm IS 'Mensaje de error de PostgreSQL';
COMMENT ON COLUMN aud_errores.usuario_bd IS 'Usuario de base de datos que ejecutó la operación';
COMMENT ON COLUMN aud_errores.fecha_evento IS 'Fecha y hora del error';
COMMENT ON COLUMN aud_errores.contexto IS 'Información adicional del contexto (JSON)';

-- Índices para consultas de errores
CREATE INDEX idx_aud_errores_origen ON aud_errores(origen);
CREATE INDEX idx_aud_errores_fecha ON aud_errores(fecha_evento);
CREATE INDEX idx_aud_errores_usuario ON aud_errores(usuario_bd);


