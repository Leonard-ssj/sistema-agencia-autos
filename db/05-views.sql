
CREATE OR REPLACE VIEW vw_ventas_mes_marca AS
SELECT 
    EXTRACT(YEAR FROM v.fecha_venta)::INT AS anio,
    EXTRACT(MONTH FROM v.fecha_venta)::INT AS mes,
    TO_CHAR(v.fecha_venta, 'Month') AS mes_nombre,
    -- PIVOT: Una columna por cada marca principal
    SUM(CASE WHEN m.nombre = 'Toyota' THEN v.total_venta ELSE 0 END) AS toyota,
    SUM(CASE WHEN m.nombre = 'Honda' THEN v.total_venta ELSE 0 END) AS honda,
    SUM(CASE WHEN m.nombre = 'Ford' THEN v.total_venta ELSE 0 END) AS ford,
    SUM(CASE WHEN m.nombre = 'Chevrolet' THEN v.total_venta ELSE 0 END) AS chevrolet,
    SUM(CASE WHEN m.nombre = 'Nissan' THEN v.total_venta ELSE 0 END) AS nissan,
    SUM(CASE WHEN m.nombre = 'Mazda' THEN v.total_venta ELSE 0 END) AS mazda,
    SUM(CASE WHEN m.nombre = 'Volkswagen' THEN v.total_venta ELSE 0 END) AS volkswagen,
    SUM(CASE WHEN m.nombre NOT IN ('Toyota', 'Honda', 'Ford', 'Chevrolet', 'Nissan', 'Mazda', 'Volkswagen') 
        THEN v.total_venta ELSE 0 END) AS otras_marcas,
    -- Total general del mes
    SUM(v.total_venta) AS total_mes,
    -- Cantidad de ventas
    COUNT(v.id) AS cantidad_ventas
FROM venta v
INNER JOIN detalle_venta dv ON v.id = dv.venta_id
INNER JOIN vehiculo vh ON dv.vehiculo_id = vh.id
INNER JOIN marca m ON vh.marca_id = m.id
WHERE v.estado_venta = 'ACTIVA'
GROUP BY 
    EXTRACT(YEAR FROM v.fecha_venta),
    EXTRACT(MONTH FROM v.fecha_venta),
    TO_CHAR(v.fecha_venta, 'Month')
ORDER BY anio DESC, mes DESC;

COMMENT ON VIEW vw_ventas_mes_marca IS 
'Vista PIVOT que muestra ventas por mes y marca. Cada marca tiene su propia columna con el total de ventas.';

-- Vista 2: Ventas detalladas por marca y mes (sin PIVOT, más flexible)
-- Esta vista es más flexible para consultas dinámicas

CREATE OR REPLACE VIEW vw_ventas_marca_mes_detalle AS
SELECT 
    EXTRACT(YEAR FROM v.fecha_venta)::INT AS anio,
    EXTRACT(MONTH FROM v.fecha_venta)::INT AS mes,
    TO_CHAR(v.fecha_venta, 'TMMonth') AS mes_nombre,
    m.nombre AS marca,
    COUNT(DISTINCT v.id) AS cantidad_ventas,
    COUNT(dv.id) AS cantidad_vehiculos,
    SUM(v.total_venta) AS total_ventas,
    AVG(v.total_venta) AS promedio_venta,
    SUM(v.descuento_aplicado) AS total_descuentos
FROM venta v
INNER JOIN detalle_venta dv ON v.id = dv.venta_id
INNER JOIN vehiculo vh ON dv.vehiculo_id = vh.id
INNER JOIN marca m ON vh.marca_id = m.id
WHERE v.estado_venta = 'ACTIVA'
GROUP BY 
    EXTRACT(YEAR FROM v.fecha_venta),
    EXTRACT(MONTH FROM v.fecha_venta),
    TO_CHAR(v.fecha_venta, 'TMMonth'),
    m.nombre
ORDER BY anio DESC, mes DESC, total_ventas DESC;

COMMENT ON VIEW vw_ventas_marca_mes_detalle IS 
'Vista detallada de ventas por marca y mes sin PIVOT. Más flexible para consultas dinámicas.';

-- Vista 3: Top marcas por año con RANKING
-- Requisito: Aplicación de RANKING para obtener el Top 5 marcas más vendidas del año

CREATE OR REPLACE VIEW vw_top_marcas_anio AS
SELECT 
    anio,
    marca,
    total_ventas,
    cantidad_ventas,
    cantidad_vehiculos,
    promedio_venta,
    -- RANK: Posición por total de ventas (permite empates)
    RANK() OVER (PARTITION BY anio ORDER BY total_ventas DESC) AS posicion_rank,
    -- DENSE_RANK: Posición sin saltos en caso de empates
    DENSE_RANK() OVER (PARTITION BY anio ORDER BY total_ventas DESC) AS posicion_dense,
    -- ROW_NUMBER: Posición única (sin empates)
    ROW_NUMBER() OVER (PARTITION BY anio ORDER BY total_ventas DESC, cantidad_ventas DESC) AS posicion_row,
    -- Porcentaje del total del año
    ROUND(
        (total_ventas * 100.0) / SUM(total_ventas) OVER (PARTITION BY anio),
        2
    ) AS porcentaje_del_anio
FROM (
    SELECT 
        EXTRACT(YEAR FROM v.fecha_venta)::INT AS anio,
        m.nombre AS marca,
        SUM(v.total_venta) AS total_ventas,
        COUNT(DISTINCT v.id) AS cantidad_ventas,
        COUNT(dv.id) AS cantidad_vehiculos,
        AVG(v.total_venta) AS promedio_venta
    FROM venta v
    INNER JOIN detalle_venta dv ON v.id = dv.venta_id
    INNER JOIN vehiculo vh ON dv.vehiculo_id = vh.id
    INNER JOIN marca m ON vh.marca_id = m.id
    WHERE v.estado_venta = 'ACTIVA'
    GROUP BY 
        EXTRACT(YEAR FROM v.fecha_venta),
        m.nombre
) AS ventas_por_marca
ORDER BY anio DESC, posicion_rank ASC;

COMMENT ON VIEW vw_top_marcas_anio IS 
'Vista con RANKING de marcas más vendidas por año. Incluye RANK, DENSE_RANK y ROW_NUMBER para diferentes tipos de ranking.';

-- Vista 4: Top 5 marcas (filtrada)
-- Vista específica para obtener solo el Top 5

CREATE OR REPLACE VIEW vw_top5_marcas AS
SELECT 
    anio,
    marca,
    total_ventas,
    cantidad_ventas,
    cantidad_vehiculos,
    promedio_venta,
    posicion_rank AS posicion,
    porcentaje_del_anio
FROM vw_top_marcas_anio
WHERE posicion_rank <= 5
ORDER BY anio DESC, posicion_rank ASC;

COMMENT ON VIEW vw_top5_marcas IS 
'Vista filtrada que muestra solo el Top 5 de marcas más vendidas por año.';

-- Vista 5: Ranking de empleados por ventas
-- Vista adicional con RANKING de empleados

CREATE OR REPLACE VIEW vw_ranking_empleados AS
SELECT 
    e.id AS empleado_id,
    e.nombre_completo,
    e.puesto,
    COUNT(DISTINCT v.id) AS cantidad_ventas,
    SUM(v.total_venta) AS total_ventas,
    AVG(v.total_venta) AS promedio_venta,
    -- RANK por total de ventas
    RANK() OVER (ORDER BY SUM(v.total_venta) DESC) AS posicion_por_monto,
    -- RANK por cantidad de ventas
    RANK() OVER (ORDER BY COUNT(DISTINCT v.id) DESC) AS posicion_por_cantidad,
    -- Clasificación usando CASE
    CASE 
        WHEN SUM(v.total_venta) >= 1000000 THEN 'ESTRELLA'
        WHEN SUM(v.total_venta) >= 500000 THEN 'DESTACADO'
        WHEN SUM(v.total_venta) >= 100000 THEN 'REGULAR'
        ELSE 'NUEVO'
    END AS clasificacion
FROM empleado e
LEFT JOIN venta v ON e.id = v.empleado_id AND v.estado_venta = 'ACTIVA'
WHERE e.estado = 'ACTIVO'
GROUP BY e.id, e.nombre_completo, e.puesto
ORDER BY total_ventas DESC NULLS LAST;

COMMENT ON VIEW vw_ranking_empleados IS 
'Ranking de empleados por desempeño en ventas. Incluye clasificación con CASE.';

-- Vista 6: Inventario actual con análisis
-- Vista con subconsultas y análisis de inventario

CREATE OR REPLACE VIEW vw_inventario_analisis AS
SELECT 
    v.id AS vehiculo_id,
    m.nombre AS marca,
    v.modelo,
    v.anio,
    v.precio,
    v.color,
    tv.nombre AS tipo_vehiculo,
    v.estado_disponibilidad,
    v.fecha_ingreso,
    CURRENT_DATE - v.fecha_ingreso AS dias_en_inventario,
    -- Clasificación por días en inventario usando CASE
    CASE 
        WHEN CURRENT_DATE - v.fecha_ingreso > 180 THEN 'CRITICO'
        WHEN CURRENT_DATE - v.fecha_ingreso > 90 THEN 'ALTO'
        WHEN CURRENT_DATE - v.fecha_ingreso > 30 THEN 'MEDIO'
        ELSE 'NUEVO'
    END AS nivel_inventario,
    -- Comparación con precio promedio de la marca (subconsulta)
    (
        SELECT AVG(v2.precio)
        FROM vehiculo v2
        WHERE v2.marca_id = v.marca_id
    ) AS precio_promedio_marca,
    -- Diferencia con el promedio
    v.precio - (
        SELECT AVG(v2.precio)
        FROM vehiculo v2
        WHERE v2.marca_id = v.marca_id
    ) AS diferencia_promedio
FROM vehiculo v
INNER JOIN marca m ON v.marca_id = m.id
INNER JOIN tipo_vehiculo tv ON v.tipo_vehiculo_id = tv.id
ORDER BY v.estado_disponibilidad, dias_en_inventario DESC;

COMMENT ON VIEW vw_inventario_analisis IS 
'Análisis completo del inventario con subconsultas, CASE y comparaciones de precios.';

-- Vista 7: Resumen de auditoría
-- Vista para consultar auditoría de forma consolidada

CREATE OR REPLACE VIEW vw_auditoria_consolidada AS
SELECT 
    'VENTA' AS tipo_entidad,
    av.venta_id AS entidad_id,
    av.accion,
    av.usuario_bd,
    av.fecha_evento,
    av.old_data,
    av.new_data
FROM aud_ventas av
UNION ALL
SELECT 
    'VEHICULO' AS tipo_entidad,
    avh.vehiculo_id AS entidad_id,
    avh.accion,
    avh.usuario_bd,
    avh.fecha_evento,
    avh.old_data,
    avh.new_data
FROM aud_vehiculos avh
ORDER BY fecha_evento DESC;

COMMENT ON VIEW vw_auditoria_consolidada IS 
'Vista consolidada de auditoría de ventas y vehículos para consultas unificadas.';

-- Funciones auxiliares para consultar vistas

-- Función para obtener ventas PIVOT de un año específico
CREATE OR REPLACE FUNCTION obtener_ventas_pivot(p_anio INT)
RETURNS TABLE (
    mes INT,
    mes_nombre TEXT,
    toyota NUMERIC,
    honda NUMERIC,
    ford NUMERIC,
    chevrolet NUMERIC,
    nissan NUMERIC,
    mazda NUMERIC,
    volkswagen NUMERIC,
    otras_marcas NUMERIC,
    total_mes NUMERIC,
    cantidad_ventas BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        v.mes,
        v.mes_nombre,
        v.toyota,
        v.honda,
        v.ford,
        v.chevrolet,
        v.nissan,
        v.mazda,
        v.volkswagen,
        v.otras_marcas,
        v.total_mes,
        v.cantidad_ventas
    FROM vw_ventas_mes_marca v
    WHERE v.anio = p_anio
    ORDER BY v.mes;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION obtener_ventas_pivot IS 
'Obtiene el reporte PIVOT de ventas por mes y marca para un año específico.';

-- Función para obtener Top 5 marcas de un año
CREATE OR REPLACE FUNCTION obtener_top5_marcas(p_anio INT)
RETURNS TABLE (
    posicion INT,
    marca VARCHAR(50),
    total_ventas NUMERIC,
    cantidad_ventas BIGINT,
    porcentaje_del_anio NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.posicion_rank::INT AS posicion,
        t.marca,
        t.total_ventas,
        t.cantidad_ventas,
        t.porcentaje_del_anio
    FROM vw_top_marcas_anio t
    WHERE t.anio = p_anio AND t.posicion_rank <= 5
    ORDER BY t.posicion_rank;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION obtener_top5_marcas IS 
'Obtiene el Top 5 de marcas más vendidas para un año específico usando RANK.';


