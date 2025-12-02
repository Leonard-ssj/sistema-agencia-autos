
DROP TABLE IF EXISTS detalle_venta CASCADE;
DROP TABLE IF EXISTS venta CASCADE;
DROP TABLE IF EXISTS vehiculo CASCADE;
DROP TABLE IF EXISTS cliente CASCADE;
DROP TABLE IF EXISTS empleado CASCADE;
DROP TABLE IF EXISTS metodo_pago CASCADE;
DROP TABLE IF EXISTS tipo_documento CASCADE;
DROP TABLE IF EXISTS tipo_vehiculo CASCADE;
DROP TABLE IF EXISTS marca CASCADE;

-- Tablas de catálogo

-- Catálogo: Marcas de vehículos
CREATE TABLE marca (
    id BIGSERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL UNIQUE,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE marca IS 'Catálogo de marcas de vehículos';
COMMENT ON COLUMN marca.id IS 'Identificador único de la marca';
COMMENT ON COLUMN marca.nombre IS 'Nombre de la marca (Toyota, Honda, etc.)';

-- Catálogo: Tipos de vehículos
CREATE TABLE tipo_vehiculo (
    id BIGSERIAL PRIMARY KEY,
    nombre VARCHAR(30) NOT NULL UNIQUE,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE tipo_vehiculo IS 'Catálogo de tipos de vehículos';
COMMENT ON COLUMN tipo_vehiculo.nombre IS 'Tipo de vehículo (Sedán, SUV, Pickup, etc.)';

-- Catálogo: Métodos de pago
CREATE TABLE metodo_pago (
    id BIGSERIAL PRIMARY KEY,
    nombre VARCHAR(30) NOT NULL UNIQUE,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE metodo_pago IS 'Catálogo de métodos de pago';
COMMENT ON COLUMN metodo_pago.nombre IS 'Método de pago (Contado, Crédito, etc.)';

-- Catálogo: Tipos de documento
CREATE TABLE tipo_documento (
    id BIGSERIAL PRIMARY KEY,
    nombre VARCHAR(20) NOT NULL UNIQUE,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE tipo_documento IS 'Catálogo de tipos de documento de identificación';
COMMENT ON COLUMN tipo_documento.nombre IS 'Tipo de documento (INE, Pasaporte, etc.)';


-- Tabla: Empleados
CREATE TABLE empleado (
    id BIGSERIAL PRIMARY KEY,
    nombre_completo VARCHAR(100) NOT NULL,
    puesto VARCHAR(50) NOT NULL,
    usuario VARCHAR(50) NOT NULL UNIQUE,
    contrasena VARCHAR(100) NOT NULL,
    fecha_ingreso DATE NOT NULL DEFAULT CURRENT_DATE,
    estado VARCHAR(20) NOT NULL DEFAULT 'ACTIVO',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_empleado_estado CHECK (estado IN ('ACTIVO', 'INACTIVO'))
);

COMMENT ON TABLE empleado IS 'Empleados de la agencia (vendedores, administradores)';
COMMENT ON COLUMN empleado.id IS 'Identificador único del empleado (SEQUENCE)';
COMMENT ON COLUMN empleado.estado IS 'Estado del empleado: ACTIVO o INACTIVO';

-- Índice para búsqueda por usuario
CREATE INDEX idx_empleado_usuario ON empleado(usuario);
CREATE INDEX idx_empleado_estado ON empleado(estado);

-- Tabla: Clientes
CREATE TABLE cliente (
    id BIGSERIAL PRIMARY KEY,
    nombre_completo VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    direccion VARCHAR(150),
    tipo_documento_id BIGINT NOT NULL,
    numero_documento VARCHAR(30) NOT NULL,
    fecha_registro DATE NOT NULL DEFAULT CURRENT_DATE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_cliente_tipo_documento FOREIGN KEY (tipo_documento_id) 
        REFERENCES tipo_documento(id) ON DELETE RESTRICT
);

COMMENT ON TABLE cliente IS 'Clientes de la agencia';
COMMENT ON COLUMN cliente.id IS 'Identificador único del cliente (SEQUENCE)';
COMMENT ON COLUMN cliente.email IS 'Correo electrónico (debe ser único)';
COMMENT ON COLUMN cliente.numero_documento IS 'Número de documento (único por tipo)';

-- ÍNDICE ÚNICO: Email (Requisito 7)
CREATE UNIQUE INDEX idx_cliente_email ON cliente(email);

-- ÍNDICE ÚNICO COMPUESTO: Tipo documento + Número documento (Requisito 7)
CREATE UNIQUE INDEX idx_cliente_documento ON cliente(tipo_documento_id, numero_documento);

-- Índices adicionales para búsqueda
CREATE INDEX idx_cliente_nombre ON cliente(nombre_completo);
CREATE INDEX idx_cliente_fecha_registro ON cliente(fecha_registro);

-- Tabla: Vehículos
CREATE TABLE vehiculo (
    id BIGSERIAL PRIMARY KEY,
    marca_id BIGINT NOT NULL,
    modelo VARCHAR(50) NOT NULL,
    anio INT NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    color VARCHAR(30) NOT NULL,
    tipo_vehiculo_id BIGINT NOT NULL,
    vin VARCHAR(17) UNIQUE,
    estado_disponibilidad VARCHAR(20) NOT NULL DEFAULT 'DISPONIBLE',
    fecha_ingreso DATE NOT NULL DEFAULT CURRENT_DATE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_vehiculo_marca FOREIGN KEY (marca_id) 
        REFERENCES marca(id) ON DELETE RESTRICT,
    CONSTRAINT fk_vehiculo_tipo FOREIGN KEY (tipo_vehiculo_id) 
        REFERENCES tipo_vehiculo(id) ON DELETE RESTRICT,
    CONSTRAINT chk_vehiculo_anio CHECK (anio >= 1900 AND anio <= 2100),
    CONSTRAINT chk_vehiculo_precio CHECK (precio > 0),
    CONSTRAINT chk_vehiculo_estado CHECK (estado_disponibilidad IN ('DISPONIBLE', 'VENDIDO', 'RESERVADO'))
);

COMMENT ON TABLE vehiculo IS 'Inventario de vehículos de la agencia';
COMMENT ON COLUMN vehiculo.id IS 'Identificador único del vehículo (SEQUENCE)';
COMMENT ON COLUMN vehiculo.vin IS 'Número de identificación vehicular (único)';
COMMENT ON COLUMN vehiculo.estado_disponibilidad IS 'Estado: DISPONIBLE, VENDIDO, RESERVADO';

-- ÍNDICE COMPUESTO: Marca + Modelo (Requisito 7)
CREATE INDEX idx_vehiculo_marca_modelo ON vehiculo(marca_id, modelo);

-- Índices adicionales para búsqueda y filtrado
CREATE INDEX idx_vehiculo_estado ON vehiculo(estado_disponibilidad);
CREATE INDEX idx_vehiculo_tipo ON vehiculo(tipo_vehiculo_id);
CREATE INDEX idx_vehiculo_precio ON vehiculo(precio);
CREATE INDEX idx_vehiculo_anio ON vehiculo(anio);

-- Tabla: Ventas
CREATE TABLE venta (
    id BIGSERIAL PRIMARY KEY,
    cliente_id BIGINT NOT NULL,
    empleado_id BIGINT NOT NULL,
    metodo_pago_id BIGINT NOT NULL,
    fecha_venta DATE NOT NULL DEFAULT CURRENT_DATE,
    total_venta DECIMAL(10,2) NOT NULL,
    descuento_aplicado DECIMAL(10,2) DEFAULT 0,
    estado_venta VARCHAR(20) NOT NULL DEFAULT 'ACTIVA',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_modificacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_venta_cliente FOREIGN KEY (cliente_id) 
        REFERENCES cliente(id) ON DELETE RESTRICT,
    CONSTRAINT fk_venta_empleado FOREIGN KEY (empleado_id) 
        REFERENCES empleado(id) ON DELETE RESTRICT,
    CONSTRAINT fk_venta_metodo_pago FOREIGN KEY (metodo_pago_id) 
        REFERENCES metodo_pago(id) ON DELETE RESTRICT,
    CONSTRAINT chk_venta_total CHECK (total_venta >= 0),
    CONSTRAINT chk_venta_descuento CHECK (descuento_aplicado >= 0),
    CONSTRAINT chk_venta_estado CHECK (estado_venta IN ('ACTIVA', 'CANCELADA', 'PENDIENTE'))
);

COMMENT ON TABLE venta IS 'Registro de ventas realizadas';
COMMENT ON COLUMN venta.id IS 'Identificador único de la venta (SEQUENCE)';
COMMENT ON COLUMN venta.estado_venta IS 'Estado: ACTIVA, CANCELADA, PENDIENTE';
COMMENT ON COLUMN venta.descuento_aplicado IS 'Monto de descuento aplicado';

-- ÍNDICES: Estado y Fecha de venta (Requisito 7)
CREATE INDEX idx_venta_estado ON venta(estado_venta);
CREATE INDEX idx_venta_fecha ON venta(fecha_venta);

-- Índices adicionales para reportes
CREATE INDEX idx_venta_cliente ON venta(cliente_id);
CREATE INDEX idx_venta_empleado ON venta(empleado_id);
CREATE INDEX idx_venta_fecha_estado ON venta(fecha_venta, estado_venta);

-- Tabla: Detalle de Ventas
CREATE TABLE detalle_venta (
    id BIGSERIAL PRIMARY KEY,
    venta_id BIGINT NOT NULL,
    vehiculo_id BIGINT NOT NULL,
    cantidad INT NOT NULL DEFAULT 1,
    precio_unitario DECIMAL(10,2) NOT NULL,
    subtotal DECIMAL(10,2) NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_detalle_venta FOREIGN KEY (venta_id) 
        REFERENCES venta(id) ON DELETE CASCADE,
    CONSTRAINT fk_detalle_vehiculo FOREIGN KEY (vehiculo_id) 
        REFERENCES vehiculo(id) ON DELETE RESTRICT,
    CONSTRAINT chk_detalle_cantidad CHECK (cantidad > 0),
    CONSTRAINT chk_detalle_precio CHECK (precio_unitario > 0),
    CONSTRAINT chk_detalle_subtotal CHECK (subtotal >= 0)
);

COMMENT ON TABLE detalle_venta IS 'Detalle de vehículos vendidos en cada venta';
COMMENT ON COLUMN detalle_venta.id IS 'Identificador único del detalle (SEQUENCE)';
COMMENT ON COLUMN detalle_venta.cantidad IS 'Cantidad de vehículos (normalmente 1)';
COMMENT ON COLUMN detalle_venta.subtotal IS 'Resultado de cantidad × precio_unitario';

-- ÍNDICE ÚNICO: Evitar duplicar vehículo en misma venta
CREATE UNIQUE INDEX idx_detalle_venta_vehiculo ON detalle_venta(venta_id, vehiculo_id);

-- Índices para consultas
CREATE INDEX idx_detalle_venta ON detalle_venta(venta_id);
CREATE INDEX idx_detalle_vehiculo ON detalle_venta(vehiculo_id);


