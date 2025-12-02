

CREATE OR REPLACE FUNCTION registrar_venta(
    p_cliente_id BIGINT,
    p_empleado_id BIGINT,
    p_metodo_pago_id BIGINT,
    p_vehiculo_id BIGINT,
    p_precio DECIMAL(10,2),
    p_cantidad INT DEFAULT 1,
    p_descuento_temporada BOOLEAN DEFAULT FALSE,
    p_cliente_frecuente BOOLEAN DEFAULT FALSE
)
RETURNS BIGINT AS $$
DECLARE
    v_venta_id BIGINT;
    v_subtotal DECIMAL(10,2);
    v_descuento DECIMAL(10,2);
    v_total DECIMAL(10,2);
    v_porcentaje_descuento DECIMAL(5,2);
    v_cliente_nombre VARCHAR(100);
    v_vehiculo_info TEXT;
BEGIN
    -- Validar que el cliente existe
    SELECT nombre_completo INTO v_cliente_nombre
    FROM cliente
    WHERE id = p_cliente_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Cliente con ID % no existe', p_cliente_id;
    END IF;
    
    -- Validar que el empleado existe y está activo
    IF NOT EXISTS (SELECT 1 FROM empleado WHERE id = p_empleado_id AND estado = 'ACTIVO') THEN
        RAISE EXCEPTION 'Empleado con ID % no existe o no está activo', p_empleado_id;
    END IF;
    
    -- Validar que el método de pago existe
    IF NOT EXISTS (SELECT 1 FROM metodo_pago WHERE id = p_metodo_pago_id) THEN
        RAISE EXCEPTION 'Método de pago con ID % no existe', p_metodo_pago_id;
    END IF;
    
    -- Validar cantidad
    IF p_cantidad <= 0 THEN
        RAISE EXCEPTION 'La cantidad debe ser mayor a 0';
    END IF;
    
    -- Validar precio
    IF p_precio <= 0 THEN
        RAISE EXCEPTION 'El precio debe ser mayor a 0';
    END IF;
    
    -- Calcular subtotal
    v_subtotal := p_precio * p_cantidad;
    
    -- Calcular descuento (10% temporada + 5% cliente frecuente, acumulables)
    v_porcentaje_descuento := 0;
    IF p_descuento_temporada THEN
        v_porcentaje_descuento := v_porcentaje_descuento + 10.00;
    END IF;
    IF p_cliente_frecuente THEN
        v_porcentaje_descuento := v_porcentaje_descuento + 5.00;
    END IF;
    
    v_descuento := v_subtotal * (v_porcentaje_descuento / 100);
    v_total := v_subtotal - v_descuento;
    
    -- INICIAR TRANSACCIÓN EXPLÍCITA
    -- Nota: En PostgreSQL las funciones ya están en una transacción implícita,
    -- pero documentamos el comportamiento transaccional
    
    -- Insertar la venta
    INSERT INTO venta (
        cliente_id,
        empleado_id,
        metodo_pago_id,
        fecha_venta,
        total_venta,
        descuento_aplicado,
        estado_venta
    ) VALUES (
        p_cliente_id,
        p_empleado_id,
        p_metodo_pago_id,
        CURRENT_DATE,
        v_total,
        v_descuento,
        'ACTIVA'
    ) RETURNING id INTO v_venta_id;
    
    -- Insertar el detalle de la venta
    -- Esto disparará los triggers:
    -- 1. trg_check_disponibilidad (valida que el vehículo esté disponible)
    -- 2. trg_update_estado_vehiculo (actualiza estado a VENDIDO)
    INSERT INTO detalle_venta (
        venta_id,
        vehiculo_id,
        cantidad,
        precio_unitario,
        subtotal
    ) VALUES (
        v_venta_id,
        p_vehiculo_id,
        p_cantidad,
        p_precio,
        v_subtotal
    );
    
    -- Si llegamos aquí, todo salió bien (COMMIT implícito)
    RAISE NOTICE 'Venta registrada exitosamente. ID: %, Total: $%, Descuento: $%', 
        v_venta_id, v_total, v_descuento;
    
    RETURN v_venta_id;
    
EXCEPTION
    WHEN OTHERS THEN
        -- Capturar cualquier error (TRY/CATCH)
        -- Registrar el error en la tabla de auditoría
        INSERT INTO aud_errores (
            origen,
            detalle,
            sqlstate,
            sqlerrm,
            usuario_bd,
            fecha_evento,
            contexto
        ) VALUES (
            'registrar_venta',
            format('Error al registrar venta. Cliente: %s, Vehículo: %s', p_cliente_id, p_vehiculo_id),
            SQLSTATE,
            SQLERRM,
            CURRENT_USER,
            CURRENT_TIMESTAMP,
            jsonb_build_object(
                'cliente_id', p_cliente_id,
                'empleado_id', p_empleado_id,
                'vehiculo_id', p_vehiculo_id,
                'precio', p_precio,
                'cantidad', p_cantidad
            )
        );
        
        -- NO hacer RAISE para que se haga COMMIT del error
        -- Retornar NULL para indicar fallo
        RETURN NULL;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION registrar_venta IS 
'Registra una nueva venta con validaciones, transacción atómica y manejo de errores. Aplica descuentos del 5% si es temporada o cliente frecuente.';

-- Función 2: Cancelar venta
-- Cancela una venta y libera automáticamente los vehículos asociados
-- Incluye manejo de errores con transacción atómica

CREATE OR REPLACE FUNCTION cancelar_venta(
    p_venta_id BIGINT
)
RETURNS BOOLEAN AS $$
DECLARE
    v_estado_actual VARCHAR(20);
    v_vehiculo_id BIGINT;
    v_count INT;
BEGIN
    -- Validar que la venta existe
    SELECT estado_venta INTO v_estado_actual
    FROM venta
    WHERE id = p_venta_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Venta con ID % no existe', p_venta_id;
    END IF;
    
    -- Validar que la venta no esté ya cancelada
    IF v_estado_actual = 'CANCELADA' THEN
        RAISE EXCEPTION 'La venta con ID % ya está cancelada', p_venta_id;
    END IF;
    
    -- INICIAR TRANSACCIÓN (implícita en PostgreSQL)
    
    -- Actualizar el estado de la venta a CANCELADA
    UPDATE venta
    SET estado_venta = 'CANCELADA',
        fecha_modificacion = CURRENT_TIMESTAMP
    WHERE id = p_venta_id;
    
    -- Liberar los vehículos asociados (regresarlos a DISPONIBLE)
    UPDATE vehiculo
    SET estado_disponibilidad = 'DISPONIBLE',
        fecha_modificacion = CURRENT_TIMESTAMP
    WHERE id IN (
        SELECT vehiculo_id
        FROM detalle_venta
        WHERE venta_id = p_venta_id
    );
    
    -- Obtener cantidad de vehículos liberados
    GET DIAGNOSTICS v_count = ROW_COUNT;
    
    -- Si llegamos aquí, todo salió bien (COMMIT implícito)
    RAISE NOTICE 'Venta % cancelada exitosamente. % vehículo(s) liberado(s)', 
        p_venta_id, v_count;
    
    RETURN TRUE;
    
EXCEPTION
    WHEN OTHERS THEN
        -- Capturar cualquier error (TRY/CATCH)
        -- Registrar el error en la tabla de auditoría
        INSERT INTO aud_errores (
            origen,
            detalle,
            sqlstate,
            sqlerrm,
            usuario_bd,
            fecha_evento,
            contexto
        ) VALUES (
            'cancelar_venta',
            format('Error al cancelar venta ID: %s', p_venta_id),
            SQLSTATE,
            SQLERRM,
            CURRENT_USER,
            CURRENT_TIMESTAMP,
            jsonb_build_object('venta_id', p_venta_id)
        );
        
        -- NO hacer RAISE para que se haga COMMIT del error
        -- Retornar FALSE para indicar fallo
        RETURN FALSE;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION cancelar_venta IS 
'Cancela una venta y libera automáticamente los vehículos asociados (regresa a DISPONIBLE). Incluye manejo de errores con TRY/CATCH.';

-- Función 3: Historial de compras de un cliente
-- Consulta el historial completo de compras con información detallada

CREATE OR REPLACE FUNCTION historial_cliente(
    p_cliente_id BIGINT
)
RETURNS TABLE (
    venta_id BIGINT,
    fecha_venta DATE,
    total_venta DECIMAL(10,2),
    descuento_aplicado DECIMAL(10,2),
    estado_venta VARCHAR(20),
    metodo_pago VARCHAR(30),
    empleado_nombre VARCHAR(100),
    vehiculo_marca VARCHAR(50),
    vehiculo_modelo VARCHAR(50),
    vehiculo_anio INT,
    precio_unitario DECIMAL(10,2)
) AS $$
BEGIN
    -- Validar que el cliente existe
    IF NOT EXISTS (SELECT 1 FROM cliente WHERE id = p_cliente_id) THEN
        RAISE EXCEPTION 'Cliente con ID % no existe', p_cliente_id;
    END IF;
    
    -- Retornar el historial de compras con JOINs
    RETURN QUERY
    SELECT 
        v.id AS venta_id,
        v.fecha_venta,
        v.total_venta,
        v.descuento_aplicado,
        v.estado_venta,
        mp.nombre AS metodo_pago,
        e.nombre_completo AS empleado_nombre,
        m.nombre AS vehiculo_marca,
        vh.modelo AS vehiculo_modelo,
        vh.anio AS vehiculo_anio,
        dv.precio_unitario
    FROM venta v
    INNER JOIN metodo_pago mp ON v.metodo_pago_id = mp.id
    INNER JOIN empleado e ON v.empleado_id = e.id
    INNER JOIN detalle_venta dv ON v.id = dv.venta_id
    INNER JOIN vehiculo vh ON dv.vehiculo_id = vh.id
    INNER JOIN marca m ON vh.marca_id = m.id
    WHERE v.cliente_id = p_cliente_id
    ORDER BY v.fecha_venta DESC, v.id DESC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION historial_cliente IS 
'Consulta el historial completo de compras de un cliente con información detallada de vehículos y ventas.';

-- Función 4: Disponibilidad de vehículos por marca y tipo
-- Consulta vehículos disponibles filtrados por marca y tipo

CREATE OR REPLACE FUNCTION disponibilidad_por_marca_tipo(
    p_marca_id BIGINT DEFAULT NULL,
    p_tipo_vehiculo_id BIGINT DEFAULT NULL,
    p_solo_disponibles BOOLEAN DEFAULT TRUE
)
RETURNS TABLE (
    vehiculo_id BIGINT,
    marca VARCHAR(50),
    modelo VARCHAR(50),
    anio INT,
    precio DECIMAL(10,2),
    color VARCHAR(30),
    tipo_vehiculo VARCHAR(30),
    estado_disponibilidad VARCHAR(20),
    dias_en_inventario INT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        v.id AS vehiculo_id,
        m.nombre AS marca,
        v.modelo,
        v.anio,
        v.precio,
        v.color,
        tv.nombre AS tipo_vehiculo,
        v.estado_disponibilidad,
        CURRENT_DATE - v.fecha_ingreso AS dias_en_inventario
    FROM vehiculo v
    INNER JOIN marca m ON v.marca_id = m.id
    INNER JOIN tipo_vehiculo tv ON v.tipo_vehiculo_id = tv.id
    WHERE 
        (p_marca_id IS NULL OR v.marca_id = p_marca_id)
        AND (p_tipo_vehiculo_id IS NULL OR v.tipo_vehiculo_id = p_tipo_vehiculo_id)
        AND (NOT p_solo_disponibles OR v.estado_disponibilidad = 'DISPONIBLE')
    ORDER BY m.nombre, v.modelo, v.anio DESC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION disponibilidad_por_marca_tipo IS 
'Consulta vehículos disponibles filtrados por marca y/o tipo. Incluye días en inventario.';

-- Función 5: Top marcas y modelos más vendidos
-- Genera reporte de las marcas y modelos más vendidos

CREATE OR REPLACE FUNCTION top_marcas_modelos(
    p_anio INT DEFAULT NULL,
    p_limite INT DEFAULT 10
)
RETURNS TABLE (
    marca VARCHAR(50),
    modelo VARCHAR(50),
    cantidad_vendida BIGINT,
    total_ventas DECIMAL(12,2),
    precio_promedio DECIMAL(10,2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        m.nombre AS marca,
        v.modelo,
        COUNT(dv.id) AS cantidad_vendida,
        SUM(dv.subtotal) AS total_ventas,
        AVG(dv.precio_unitario) AS precio_promedio
    FROM detalle_venta dv
    INNER JOIN vehiculo v ON dv.vehiculo_id = v.id
    INNER JOIN marca m ON v.marca_id = m.id
    INNER JOIN venta vt ON dv.venta_id = vt.id
    WHERE 
        vt.estado_venta = 'ACTIVA'
        AND (p_anio IS NULL OR EXTRACT(YEAR FROM vt.fecha_venta) = p_anio)
    GROUP BY m.nombre, v.modelo
    ORDER BY cantidad_vendida DESC, total_ventas DESC
    LIMIT p_limite;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION top_marcas_modelos IS 
'Genera reporte de las marcas y modelos más vendidos, opcionalmente filtrado por año.';

-- Función 6: Clasificar clientes por frecuencia
-- Clasifica clientes por frecuencia de compra usando CASE

CREATE OR REPLACE FUNCTION clasificar_clientes()
RETURNS TABLE (
    cliente_id BIGINT,
    nombre_completo VARCHAR(100),
    email VARCHAR(100),
    total_compras BIGINT,
    monto_total DECIMAL(12,2),
    clasificacion VARCHAR(20)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.id AS cliente_id,
        c.nombre_completo,
        c.email,
        COUNT(v.id) AS total_compras,
        COALESCE(SUM(v.total_venta), 0) AS monto_total,
        CASE 
            WHEN COUNT(v.id) >= 5 THEN 'VIP'
            WHEN COUNT(v.id) >= 3 THEN 'FRECUENTE'
            WHEN COUNT(v.id) >= 1 THEN 'REGULAR'
            ELSE 'NUEVO'
        END::VARCHAR(20) AS clasificacion
    FROM cliente c
    LEFT JOIN venta v ON c.id = v.cliente_id AND v.estado_venta = 'ACTIVA'
    GROUP BY c.id, c.nombre_completo, c.email
    ORDER BY total_compras DESC, monto_total DESC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION clasificar_clientes IS 
'Clasifica clientes por frecuencia de compra usando CASE: VIP (5+), FRECUENTE (3-4), REGULAR (1-2), NUEVO (0).';


