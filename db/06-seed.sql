
TRUNCATE TABLE detalle_venta CASCADE;
TRUNCATE TABLE venta CASCADE;
TRUNCATE TABLE vehiculo CASCADE;
TRUNCATE TABLE cliente CASCADE;
TRUNCATE TABLE empleado CASCADE;
TRUNCATE TABLE metodo_pago CASCADE;
TRUNCATE TABLE tipo_documento CASCADE;
TRUNCATE TABLE tipo_vehiculo CASCADE;
TRUNCATE TABLE marca CASCADE;

-- Limpiar auditorías
TRUNCATE TABLE aud_ventas CASCADE;
TRUNCATE TABLE aud_vehiculos CASCADE;
TRUNCATE TABLE aud_errores CASCADE;

-- Catálogos

-- Marcas de vehículos
INSERT INTO marca (nombre) VALUES
('Toyota'),
('Honda'),
('Ford'),
('Chevrolet'),
('Nissan'),
('Mazda'),
('Volkswagen'),
('Hyundai'),
('Kia'),
('BMW');

-- Tipos de vehículos
INSERT INTO tipo_vehiculo (nombre) VALUES
('Sedán'),
('SUV'),
('Pickup'),
('Hatchback'),
('Coupé'),
('Minivan');

-- Métodos de pago
INSERT INTO metodo_pago (nombre) VALUES
('Contado'),
('Crédito'),
('Transferencia'),
('Tarjeta de Débito');

-- Tipos de documento
INSERT INTO tipo_documento (nombre) VALUES
('INE'),
('Pasaporte'),
('Licencia de Conducir');

-- Empleados

INSERT INTO empleado (nombre_completo, puesto, usuario, contrasena, fecha_ingreso, estado) VALUES
('Juan Carlos Pérez', 'Gerente de Ventas', 'jperez', 'hashed_password_1', '2023-01-15', 'ACTIVO'),
('María González López', 'Vendedor Senior', 'mgonzalez', 'hashed_password_2', '2023-03-20', 'ACTIVO'),
('Roberto Martínez', 'Vendedor', 'rmartinez', 'hashed_password_3', '2024-01-10', 'ACTIVO'),
('Ana Sofía Ramírez', 'Vendedor', 'aramirez', 'hashed_password_4', '2024-06-01', 'ACTIVO'),
('Luis Fernando Torres', 'Administrador', 'ltorres', 'hashed_password_5', '2022-11-01', 'ACTIVO');

-- Clientes

INSERT INTO cliente (nombre_completo, email, telefono, direccion, tipo_documento_id, numero_documento, fecha_registro) VALUES
('Carlos Alberto Sánchez', 'carlos.sanchez@email.com', '5551234567', 'Av. Reforma 123, CDMX', 1, 'SANC850615HDFRRL01', '2024-01-15'),
('Laura Patricia Hernández', 'laura.hernandez@email.com', '5552345678', 'Calle Juárez 456, Guadalajara', 1, 'HERL900320MJCRRS08', '2024-02-20'),
('Miguel Ángel Rodríguez', 'miguel.rodriguez@email.com', '5553456789', 'Blvd. Díaz Ordaz 789, Monterrey', 1, 'RODM880712HNLDGR09', '2024-03-10'),
('Patricia Gómez Flores', 'patricia.gomez@email.com', '5554567890', 'Av. Universidad 321, Puebla', 1, 'GOFP920825MDFMLT03', '2024-03-25'),
('Jorge Luis Martínez', 'jorge.martinez@email.com', '5555678901', 'Calle Morelos 654, Querétaro', 2, 'P123456789', '2024-04-05'),
('Ana María López', 'ana.lopez@email.com', '5556789012', 'Av. Insurgentes 987, CDMX', 1, 'LOPA870415MDFPNN02', '2024-04-20'),
('Ricardo Fernández', 'ricardo.fernandez@email.com', '5557890123', 'Calle Hidalgo 147, León', 1, 'FERR910530HGTRNC04', '2024-05-10'),
('Gabriela Torres Ruiz', 'gabriela.torres@email.com', '5558901234', 'Av. Constitución 258, Tijuana', 1, 'TORG930218MBCRRL05', '2024-05-25'),
('Fernando Ramírez', 'fernando.ramirez@email.com', '5559012345', 'Blvd. Kukulcán 369, Cancún', 3, 'LIC987654321', '2024-06-15'),
('Sofía Mendoza Castro', 'sofia.mendoza@email.com', '5550123456', 'Calle Zaragoza 741, Mérida', 1, 'MECS950810MYNNFT06', '2024-07-01'),
('Diego Alejandro Cruz', 'diego.cruz@email.com', '5551230987', 'Av. Revolución 852, CDMX', 1, 'CRUD880922HDFRRL07', '2024-07-20'),
('Valeria Jiménez', 'valeria.jimenez@email.com', '5552341098', 'Calle Madero 963, Guadalajara', 1, 'JIMV920505MJCMNL08', '2024-08-10'),
('Andrés Morales', 'andres.morales@email.com', '5553452109', 'Blvd. Lázaro Cárdenas 159, Morelia', 1, 'MORA860730HMNRLN09', '2024-08-25'),
('Carolina Vega', 'carolina.vega@email.com', '5554563210', 'Av. Juárez 357, Toluca', 2, 'P987654321', '2024-09-05'),
('Héctor Ramírez', 'hector.ramirez@email.com', '5555674321', 'Calle Allende 486, Aguascalientes', 1, 'RAMH910615HGTMLC10', '2024-09-20'),
('Daniela Ortiz', 'daniela.ortiz@email.com', '5556785432', 'Av. Tecnológico 597, Chihuahua', 1, 'ORTD940320MCHRTL11', '2024-10-01'),
('Pablo Castillo', 'pablo.castillo@email.com', '5557896543', 'Blvd. Venustiano Carranza 618, Saltillo', 1, 'CASP870825HCSSTL12', '2024-10-15'),
('Mariana Silva', 'mariana.silva@email.com', '5558907654', 'Calle Independencia 729, Durango', 1, 'SILM930510MDFLVR13', '2024-10-25'),
('Javier Núñez', 'javier.nunez@email.com', '5559018765', 'Av. López Mateos 840, Hermosillo', 3, 'LIC123456789', '2024-11-01'),
('Isabella Rojas', 'isabella.rojas@email.com', '5550129876', 'Calle Guerrero 951, Culiacán', 1, 'ROJI960218MSJRSL14', '2024-11-10');

-- Vehículos

-- Toyota (10 vehículos)
INSERT INTO vehiculo (marca_id, modelo, anio, precio, color, tipo_vehiculo_id, vin, estado_disponibilidad, fecha_ingreso) VALUES
(1, 'Corolla', 2024, 385000.00, 'Blanco', 1, '1HGBH41JXMN109186', 'DISPONIBLE', '2024-01-10'),
(1, 'Camry', 2024, 520000.00, 'Negro', 1, '1HGBH41JXMN109187', 'DISPONIBLE', '2024-01-15'),
(1, 'RAV4', 2023, 485000.00, 'Plata', 2, '1HGBH41JXMN109188', 'DISPONIBLE', '2024-02-01'),
(1, 'Hilux', 2024, 620000.00, 'Rojo', 3, '1HGBH41JXMN109189', 'DISPONIBLE', '2024-02-10'),
(1, 'Tacoma', 2023, 580000.00, 'Azul', 3, '1HGBH41JXMN109190', 'DISPONIBLE', '2024-03-01'),
(1, 'Highlander', 2024, 685000.00, 'Gris', 2, '1HGBH41JXMN109191', 'DISPONIBLE', '2024-03-15'),
(1, 'Prius', 2024, 425000.00, 'Verde', 1, '1HGBH41JXMN109192', 'DISPONIBLE', '2024-04-01'),
(1, 'Yaris', 2023, 285000.00, 'Blanco', 4, '1HGBH41JXMN109193', 'DISPONIBLE', '2024-04-20'),
(1, 'Sienna', 2024, 625000.00, 'Plata', 6, '1HGBH41JXMN109194', 'DISPONIBLE', '2024-05-01'),
(1, '4Runner', 2023, 720000.00, 'Negro', 2, '1HGBH41JXMN109195', 'DISPONIBLE', '2024-05-15');

-- Honda (8 vehículos)
INSERT INTO vehiculo (marca_id, modelo, anio, precio, color, tipo_vehiculo_id, vin, estado_disponibilidad, fecha_ingreso) VALUES
(2, 'Civic', 2024, 395000.00, 'Azul', 1, '2HGBH41JXMN209186', 'DISPONIBLE', '2024-01-20'),
(2, 'Accord', 2024, 485000.00, 'Blanco', 1, '2HGBH41JXMN209187', 'DISPONIBLE', '2024-02-05'),
(2, 'CR-V', 2023, 495000.00, 'Gris', 2, '2HGBH41JXMN209188', 'DISPONIBLE', '2024-02-20'),
(2, 'HR-V', 2024, 385000.00, 'Rojo', 2, '2HGBH41JXMN209189', 'DISPONIBLE', '2024-03-10'),
(2, 'Pilot', 2023, 625000.00, 'Negro', 2, '2HGBH41JXMN209190', 'DISPONIBLE', '2024-04-05'),
(2, 'Fit', 2023, 265000.00, 'Amarillo', 4, '2HGBH41JXMN209191', 'DISPONIBLE', '2024-04-25'),
(2, 'Odyssey', 2024, 595000.00, 'Plata', 6, '2HGBH41JXMN209192', 'DISPONIBLE', '2024-05-10'),
(2, 'Ridgeline', 2023, 585000.00, 'Azul', 3, '2HGBH41JXMN209193', 'DISPONIBLE', '2024-06-01');

-- Ford (6 vehículos)
INSERT INTO vehiculo (marca_id, modelo, anio, precio, color, tipo_vehiculo_id, vin, estado_disponibilidad, fecha_ingreso) VALUES
(3, 'F-150', 2024, 685000.00, 'Negro', 3, '3HGBH41JXMN309186', 'DISPONIBLE', '2024-01-25'),
(3, 'Mustang', 2024, 725000.00, 'Rojo', 5, '3HGBH41JXMN309187', 'DISPONIBLE', '2024-02-15'),
(3, 'Explorer', 2023, 625000.00, 'Blanco', 2, '3HGBH41JXMN309188', 'DISPONIBLE', '2024-03-05'),
(3, 'Escape', 2024, 485000.00, 'Azul', 2, '3HGBH41JXMN309189', 'DISPONIBLE', '2024-04-10'),
(3, 'Ranger', 2023, 525000.00, 'Gris', 3, '3HGBH41JXMN309190', 'DISPONIBLE', '2024-05-05'),
(3, 'Bronco', 2024, 785000.00, 'Verde', 2, '3HGBH41JXMN309191', 'DISPONIBLE', '2024-06-10');

-- Chevrolet (6 vehículos)
INSERT INTO vehiculo (marca_id, modelo, anio, precio, color, tipo_vehiculo_id, vin, estado_disponibilidad, fecha_ingreso) VALUES
(4, 'Silverado', 2024, 695000.00, 'Plata', 3, '4HGBH41JXMN409186', 'DISPONIBLE', '2024-02-01'),
(4, 'Tahoe', 2023, 825000.00, 'Negro', 2, '4HGBH41JXMN409187', 'DISPONIBLE', '2024-02-20'),
(4, 'Equinox', 2024, 465000.00, 'Blanco', 2, '4HGBH41JXMN409188', 'DISPONIBLE', '2024-03-15'),
(4, 'Traverse', 2023, 585000.00, 'Azul', 2, '4HGBH41JXMN409189', 'DISPONIBLE', '2024-04-15'),
(4, 'Camaro', 2024, 685000.00, 'Amarillo', 5, '4HGBH41JXMN409190', 'DISPONIBLE', '2024-05-20'),
(4, 'Colorado', 2023, 545000.00, 'Rojo', 3, '4HGBH41JXMN409191', 'DISPONIBLE', '2024-06-15');

-- Nissan (5 vehículos)
INSERT INTO vehiculo (marca_id, modelo, anio, precio, color, tipo_vehiculo_id, vin, estado_disponibilidad, fecha_ingreso) VALUES
(5, 'Versa', 2024, 285000.00, 'Blanco', 1, '5HGBH41JXMN509186', 'DISPONIBLE', '2024-03-01'),
(5, 'Sentra', 2024, 365000.00, 'Gris', 1, '5HGBH41JXMN509187', 'DISPONIBLE', '2024-03-20'),
(5, 'Altima', 2023, 445000.00, 'Negro', 1, '5HGBH41JXMN509188', 'DISPONIBLE', '2024-04-05'),
(5, 'Rogue', 2024, 485000.00, 'Azul', 2, '5HGBH41JXMN509189', 'DISPONIBLE', '2024-05-01'),
(5, 'Frontier', 2023, 525000.00, 'Plata', 3, '5HGBH41JXMN509190', 'DISPONIBLE', '2024-06-05');

-- Mazda, Volkswagen, Hyundai, Kia, BMW (5 vehículos más)
INSERT INTO vehiculo (marca_id, modelo, anio, precio, color, tipo_vehiculo_id, vin, estado_disponibilidad, fecha_ingreso) VALUES
(6, 'CX-5', 2024, 485000.00, 'Rojo', 2, '6HGBH41JXMN609186', 'DISPONIBLE', '2024-04-01'),
(7, 'Jetta', 2024, 395000.00, 'Blanco', 1, '7HGBH41JXMN709186', 'DISPONIBLE', '2024-04-15'),
(8, 'Tucson', 2023, 425000.00, 'Gris', 2, '8HGBH41JXMN809186', 'DISPONIBLE', '2024-05-10'),
(9, 'Sportage', 2024, 445000.00, 'Azul', 2, '9HGBH41JXMN909186', 'DISPONIBLE', '2024-06-01'),
(10, 'X3', 2023, 925000.00, 'Negro', 2, 'AHGBH41JXMNA09186', 'DISPONIBLE', '2024-06-20');

-- Ventas (datos históricos de varios meses para reportes)

-- Ventas de Enero 2024
SELECT registrar_venta(1, 1, 1, 1, 385000.00, 1, FALSE, FALSE); -- Toyota Corolla
SELECT registrar_venta(2, 2, 2, 11, 395000.00, 1, TRUE, FALSE); -- Honda Civic (con descuento)
SELECT registrar_venta(3, 3, 1, 21, 685000.00, 1, FALSE, FALSE); -- Ford F-150

-- Ventas de Febrero 2024
SELECT registrar_venta(4, 1, 3, 2, 520000.00, 1, FALSE, TRUE); -- Toyota Camry (cliente frecuente)
SELECT registrar_venta(5, 2, 1, 12, 485000.00, 1, TRUE, FALSE); -- Honda Accord (temporada)
SELECT registrar_venta(6, 3, 2, 22, 725000.00, 1, FALSE, FALSE); -- Ford Mustang
SELECT registrar_venta(7, 4, 1, 27, 695000.00, 1, FALSE, FALSE); -- Chevrolet Silverado

-- Ventas de Marzo 2024
SELECT registrar_venta(8, 1, 3, 3, 485000.00, 1, TRUE, FALSE); -- Toyota RAV4
SELECT registrar_venta(9, 2, 1, 13, 495000.00, 1, FALSE, FALSE); -- Honda CR-V
SELECT registrar_venta(10, 3, 2, 23, 625000.00, 1, FALSE, TRUE); -- Ford Explorer
SELECT registrar_venta(11, 4, 1, 28, 825000.00, 1, FALSE, FALSE); -- Chevrolet Tahoe
SELECT registrar_venta(12, 1, 3, 32, 285000.00, 1, TRUE, FALSE); -- Nissan Versa

-- Ventas de Abril 2024
SELECT registrar_venta(13, 2, 1, 4, 620000.00, 1, FALSE, FALSE); -- Toyota Hilux
SELECT registrar_venta(14, 3, 2, 14, 385000.00, 1, TRUE, FALSE); -- Honda HR-V
SELECT registrar_venta(15, 4, 1, 24, 485000.00, 1, FALSE, FALSE); -- Ford Escape
SELECT registrar_venta(16, 1, 3, 29, 465000.00, 1, FALSE, TRUE); -- Chevrolet Equinox
SELECT registrar_venta(17, 2, 1, 33, 365000.00, 1, TRUE, FALSE); -- Nissan Sentra

-- Ventas de Mayo 2024
SELECT registrar_venta(18, 3, 2, 5, 580000.00, 1, FALSE, FALSE); -- Toyota Tacoma
SELECT registrar_venta(19, 4, 1, 15, 625000.00, 1, FALSE, FALSE); -- Honda Pilot
SELECT registrar_venta(20, 1, 3, 25, 525000.00, 1, TRUE, FALSE); -- Ford Ranger
SELECT registrar_venta(1, 2, 1, 30, 585000.00, 1, FALSE, TRUE); -- Chevrolet Traverse (cliente 1 segunda compra)

-- Ventas de Junio 2024
SELECT registrar_venta(2, 3, 2, 6, 685000.00, 1, FALSE, FALSE); -- Toyota Highlander (cliente 2 segunda compra)
SELECT registrar_venta(3, 4, 1, 16, 265000.00, 1, TRUE, FALSE); -- Honda Fit
SELECT registrar_venta(4, 1, 3, 26, 785000.00, 1, FALSE, FALSE); -- Ford Bronco (cliente 4 segunda compra)

-- Verificación de datos

-- Contar registros
SELECT 'Marcas' AS tabla, COUNT(*) AS total FROM marca
UNION ALL
SELECT 'Tipos de Vehículo', COUNT(*) FROM tipo_vehiculo
UNION ALL
SELECT 'Métodos de Pago', COUNT(*) FROM metodo_pago
UNION ALL
SELECT 'Tipos de Documento', COUNT(*) FROM tipo_documento
UNION ALL
SELECT 'Empleados', COUNT(*) FROM empleado
UNION ALL
SELECT 'Clientes', COUNT(*) FROM cliente
UNION ALL
SELECT 'Vehículos', COUNT(*) FROM vehiculo
UNION ALL
SELECT 'Ventas', COUNT(*) FROM venta
UNION ALL
SELECT 'Detalles de Venta', COUNT(*) FROM detalle_venta
UNION ALL
SELECT 'Auditoría Ventas', COUNT(*) FROM aud_ventas
UNION ALL
SELECT 'Auditoría Vehículos', COUNT(*) FROM aud_vehiculos;

-- Mostrar resumen de ventas
SELECT 
    TO_CHAR(fecha_venta, 'YYYY-MM') AS mes,
    COUNT(*) AS cantidad_ventas,
    SUM(total_venta) AS total_ventas,
    AVG(total_venta) AS promedio_venta
FROM venta
WHERE estado_venta = 'ACTIVA'
GROUP BY TO_CHAR(fecha_venta, 'YYYY-MM')
ORDER BY mes;

-- Mostrar vehículos vendidos vs disponibles
SELECT 
    estado_disponibilidad,
    COUNT(*) AS cantidad
FROM vehiculo
GROUP BY estado_disponibilidad;
