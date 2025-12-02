"""
Servicio de Ventas - Usa SQL directo para llamar funciones PostgreSQL
"""
from django.db import connection, DatabaseError


def registrar_venta_service(cliente_id, empleado_id, metodo_pago_id, vehiculo_id, 
                            precio, cantidad=1, descuento_temporada=False, cliente_frecuente=False):
    """
    Registra una nueva venta llamando a la función SQL registrar_venta()
    
    Returns:
        int: ID de la venta creada
    Raises:
        DatabaseError: Si hay error en la transacción (registrado en aud_errores)
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT registrar_venta(%s, %s, %s, %s, %s, %s, %s, %s)",
                [cliente_id, empleado_id, metodo_pago_id, vehiculo_id, 
                 precio, cantidad, descuento_temporada, cliente_frecuente]
            )
            result = cursor.fetchone()
            return result[0] if result else None
    except DatabaseError as e:
        # La BD ya registró el error en aud_errores
        raise DatabaseError(f"Error al registrar venta: {str(e)}")


def cancelar_venta_service(venta_id):
    """
    Cancela una venta existente llamando a la función SQL cancelar_venta()
    
    Returns:
        bool: True si se canceló correctamente
    Raises:
        DatabaseError: Si hay error en la transacción (registrado en aud_errores)
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT cancelar_venta(%s)", [venta_id])
            result = cursor.fetchone()
            return result[0] if result else False
    except DatabaseError as e:
        # La BD ya registró el error en aud_errores
        raise DatabaseError(f"Error al cancelar venta: {str(e)}")


def obtener_ventas_por_cliente(cliente_id):
    """
    Obtiene el historial de ventas de un cliente
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT v.id, v.fecha_venta, v.total_venta, v.estado_venta,
                   e.nombre_completo as empleado, mp.nombre as metodo_pago
            FROM venta v
            JOIN empleado e ON v.empleado_id = e.id
            JOIN metodo_pago mp ON v.metodo_pago_id = mp.id
            WHERE v.cliente_id = %s
            ORDER BY v.fecha_venta DESC
        """, [cliente_id])
        
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def obtener_vehiculos_de_venta(venta_id):
    """
    Obtiene los vehículos de una venta específica
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT dv.id, v.marca_id, m.nombre as marca, v.modelo, v.anio,
                   dv.cantidad, dv.precio_unitario, dv.subtotal
            FROM detalle_venta dv
            JOIN vehiculo v ON dv.vehiculo_id = v.id
            JOIN marca m ON v.marca_id = m.id
            WHERE dv.venta_id = %s
        """, [venta_id])
        
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
