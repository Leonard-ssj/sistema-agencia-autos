"""
Servicio de Reportes - Consulta vistas SQL con PIVOT y RANK
"""
from django.db import connection


def ventas_por_mes_marca(anio):
    """
    Consulta la vista vw_ventas_mes_marca para obtener reporte PIVOT
    
    Returns:
        list: Lista de diccionarios con ventas por mes y marca
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT * FROM vw_ventas_mes_marca
            WHERE anio = %s
            ORDER BY mes
        """, [anio])
        
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def top5_marcas(anio):
    """
    Consulta la vista vw_top_marcas_anio para obtener ranking con RANK()
    Filtra solo el top 5 (posicion_rank <= 5)
    
    Returns:
        list: Lista de diccionarios con top 5 marcas más vendidas
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT anio, marca, total_ventas, cantidad_ventas, 
                   cantidad_vehiculos, promedio_venta,
                   posicion_rank as posicion, porcentaje_del_anio
            FROM vw_top_marcas_anio
            WHERE anio = %s AND posicion_rank <= 5
            ORDER BY posicion_rank
        """, [anio])
        
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def obtener_disponibilidad_por_marca_tipo(fecha_desde=None, fecha_hasta=None, marca=None, tipo=None):
    """
    Obtiene la disponibilidad de vehículos agrupada por marca y tipo
    usando SQL directo para mejor rendimiento con filtros opcionales
    """
    # Construir query con filtros
    base_query = """
        SELECT m.nombre as marca, tv.nombre as tipo_vehiculo,
               COUNT(*) as cantidad_disponible,
               AVG(v.precio) as precio_promedio
        FROM vehiculo v
        JOIN marca m ON v.marca_id = m.id
        JOIN tipo_vehiculo tv ON v.tipo_vehiculo_id = tv.id
        WHERE v.estado_disponibilidad = 'DISPONIBLE'
    """
    
    conditions = []
    params = []
    
    if fecha_desde:
        conditions.append("v.fecha_ingreso >= %s")
        params.append(fecha_desde)
    
    if fecha_hasta:
        conditions.append("v.fecha_ingreso <= %s")
        params.append(fecha_hasta)
    
    if marca:
        conditions.append("m.nombre = %s")
        params.append(marca)
    
    if tipo:
        conditions.append("tv.nombre = %s")
        params.append(tipo)
    
    if conditions:
        base_query += " AND " + " AND ".join(conditions)
    
    base_query += """
        GROUP BY m.nombre, tv.nombre
        ORDER BY m.nombre, tv.nombre
    """
    
    with connection.cursor() as cursor:
        cursor.execute(base_query, params)
        
        columns = [col[0] for col in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        return results


def historial_cliente(cliente_id):
    """
    Obtiene historial completo de compras de un cliente
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT v.id as venta_id, v.fecha_venta, v.total_venta,
                   v.descuento_aplicado, v.estado_venta,
                   COUNT(dv.id) as cantidad_vehiculos,
                   STRING_AGG(CONCAT(m.nombre, ' ', ve.modelo), ', ') as vehiculos
            FROM venta v
            JOIN detalle_venta dv ON v.id = dv.venta_id
            JOIN vehiculo ve ON dv.vehiculo_id = ve.id
            JOIN marca m ON ve.marca_id = m.id
            WHERE v.cliente_id = %s
            GROUP BY v.id, v.fecha_venta, v.total_venta, v.descuento_aplicado, v.estado_venta
            ORDER BY v.fecha_venta DESC
        """, [cliente_id])
        
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
