from django.contrib import admin
from .models import (
    Marca, TipoVehiculo, MetodoPago, TipoDocumento,
    Empleado, Cliente, Vehiculo, Venta, DetalleVenta,
    AudVenta, AudVehiculo, AudErrores
)


@admin.register(Marca)
class MarcaAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'activo', 'fecha_creacion']
    list_filter = ['activo']
    search_fields = ['nombre']
    readonly_fields = ['fecha_creacion']


@admin.register(TipoVehiculo)
class TipoVehiculoAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'activo', 'fecha_creacion']
    list_filter = ['activo']
    search_fields = ['nombre']
    readonly_fields = ['fecha_creacion']


@admin.register(MetodoPago)
class MetodoPagoAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'activo', 'fecha_creacion']
    list_filter = ['activo']
    search_fields = ['nombre']
    readonly_fields = ['fecha_creacion']


@admin.register(TipoDocumento)
class TipoDocumentoAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'activo', 'fecha_creacion']
    list_filter = ['activo']
    search_fields = ['nombre']
    readonly_fields = ['fecha_creacion']


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre_completo', 'puesto', 'usuario', 'estado', 'fecha_ingreso']
    list_filter = ['estado', 'puesto', 'fecha_ingreso']
    search_fields = ['nombre_completo', 'usuario']
    readonly_fields = ['fecha_creacion', 'fecha_modificacion']
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre_completo', 'puesto')
        }),
        ('Acceso', {
            'fields': ('usuario', 'contrasena', 'estado')
        }),
        ('Fechas', {
            'fields': ('fecha_ingreso', 'fecha_creacion', 'fecha_modificacion')
        }),
    )


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre_completo', 'email', 'telefono', 'tipo_documento', 'fecha_registro', 'get_clasificacion']
    list_filter = ['tipo_documento', 'fecha_registro']
    search_fields = ['nombre_completo', 'email', 'numero_documento']
    readonly_fields = ['fecha_creacion', 'fecha_modificacion', 'ver_historial']
    actions = ['ver_clasificacion_clientes']
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre_completo', 'email', 'telefono', 'direccion')
        }),
        ('Documento', {
            'fields': ('tipo_documento', 'numero_documento')
        }),
        ('Fechas', {
            'fields': ('fecha_registro', 'fecha_creacion', 'fecha_modificacion')
        }),
        ('Historial de Compras', {
            'fields': ('ver_historial',),
            'description': 'Historial de compras del cliente (Procedimiento: historial_cliente)'
        }),
    )
    
    def get_clasificacion(self, obj):
        from django.db import connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        CASE 
                            WHEN COUNT(v.id) >= 5 THEN 'VIP'
                            WHEN COUNT(v.id) >= 3 THEN 'FRECUENTE'
                            WHEN COUNT(v.id) >= 1 THEN 'REGULAR'
                            ELSE 'NUEVO'
                        END AS clasificacion
                    FROM cliente c
                    LEFT JOIN venta v ON c.id = v.cliente_id AND v.estado_venta = 'ACTIVA'
                    WHERE c.id = %s
                    GROUP BY c.id
                """, [obj.id])
                result = cursor.fetchone()
                return result[0] if result else 'NUEVO'
        except:
            return 'N/A'
    get_clasificacion.short_description = 'Clasificacion'
    
    def ver_historial(self, obj):
        from django.db import connection
        from django.utils.html import format_html
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM historial_cliente(%s)", [obj.id])
                rows = cursor.fetchall()
                
                if not rows:
                    return "Sin compras registradas"
                
                html = '<table style="width:100%; border-collapse: collapse; margin-top:10px;">'
                html += '<tr style="background:#417690; color:white;"><th style="padding:8px;">Venta ID</th><th>Fecha</th><th>Vehiculo</th><th>Total</th><th>Estado</th></tr>'
                for row in rows:
                    # Convertir valores a tipos correctos
                    venta_id = row[0]
                    fecha = row[1]
                    marca = row[7]  # vehiculo_marca
                    modelo = row[8]  # vehiculo_modelo
                    total = float(row[2]) if row[2] else 0  # total_venta
                    estado = row[4]  # estado_venta
                    
                    html += f'<tr style="border-bottom:1px solid #ddd;">'
                    html += f'<td style="padding:8px;">{venta_id}</td>'
                    html += f'<td>{fecha}</td>'
                    html += f'<td>{marca} {modelo}</td>'
                    html += f'<td>${total:,.2f}</td>'
                    html += f'<td>{estado}</td>'
                    html += '</tr>'
                html += '</table>'
                html += f'<p style="margin-top:10px;"><strong>Total de compras: {len(rows)}</strong></p>'
                
                return format_html(html)
        except Exception as e:
            return f"Error al obtener historial: {str(e)}"
    ver_historial.short_description = 'Historial de Compras'
    
    def ver_clasificacion_clientes(self, request, queryset):
        from django.db import connection
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM clasificar_clientes()")
            rows = cursor.fetchall()
            
            vip = sum(1 for r in rows if r[3] == 'VIP')
            frecuente = sum(1 for r in rows if r[3] == 'FRECUENTE')
            regular = sum(1 for r in rows if r[3] == 'REGULAR')
            nuevo = sum(1 for r in rows if r[3] == 'NUEVO')
            
            self.message_user(
                request,
                f'Clasificacion de clientes: VIP={vip}, FRECUENTE={frecuente}, REGULAR={regular}, NUEVO={nuevo}. Total={len(rows)} clientes.'
            )
    
    ver_clasificacion_clientes.short_description = "Ver clasificacion de clientes (Procedimiento: clasificar_clientes)"


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ['id', 'marca', 'modelo', 'anio', 'precio', 'color', 'tipo_vehiculo', 'estado_disponibilidad']
    list_filter = ['marca', 'tipo_vehiculo', 'estado_disponibilidad', 'anio']
    search_fields = ['modelo', 'vin', 'color']
    readonly_fields = ['fecha_creacion', 'fecha_modificacion']
    fieldsets = (
        ('Información del Vehículo', {
            'fields': ('marca', 'modelo', 'anio', 'tipo_vehiculo')
        }),
        ('Detalles', {
            'fields': ('precio', 'color', 'vin')
        }),
        ('Estado', {
            'fields': ('estado_disponibilidad', 'fecha_ingreso')
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_modificacion')
        }),
    )


# Inline para agregar detalles de venta dentro del formulario de venta
class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 1
    fields = ['vehiculo', 'cantidad', 'precio_unitario', 'subtotal']
    readonly_fields = ['precio_unitario', 'subtotal']
    
    def get_readonly_fields(self, request, obj=None):
        # Precio y subtotal se calculan automaticamente
        return ['precio_unitario', 'subtotal']


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ['id', 'cliente', 'empleado', 'fecha_venta', 'total_venta', 'descuento_aplicado', 'estado_venta']
    list_filter = ['estado_venta', 'metodo_pago', 'fecha_venta']
    search_fields = ['cliente__nombre_completo', 'empleado__nombre_completo']
    readonly_fields = ['fecha_creacion', 'fecha_modificacion', 'total_venta']
    date_hierarchy = 'fecha_venta'
    inlines = [DetalleVentaInline]
    actions = ['cancelar_ventas_seleccionadas']
    fieldsets = (
        ('Información de la Venta', {
            'fields': ('cliente', 'empleado', 'metodo_pago', 'fecha_venta')
        }),
        ('Montos', {
            'fields': ('descuento_aplicado', 'total_venta'),
            'description': 'El total se calcula automaticamente desde los detalles de venta'
        }),
        ('Estado', {
            'fields': ('estado_venta',)
        }),
        ('Fechas', {
            'fields': ('fecha_creacion', 'fecha_modificacion')
        }),
    )
    
    def cancelar_ventas_seleccionadas(self, request, queryset):
        from django.db import connection
        
        ventas_canceladas = 0
        vehiculos_liberados = 0
        
        for venta in queryset:
            if venta.estado_venta == 'ACTIVA':
                # Usar el procedimiento almacenado de la BD
                with connection.cursor() as cursor:
                    cursor.execute("SELECT cancelar_venta(%s)", [venta.id])
                    resultado = cursor.fetchone()[0]
                    
                    if resultado:
                        ventas_canceladas += 1
                        # Contar vehiculos liberados
                        vehiculos_liberados += venta.detalles.count()
        
        if ventas_canceladas > 0:
            self.message_user(
                request,
                f'{ventas_canceladas} venta(s) cancelada(s) exitosamente. {vehiculos_liberados} vehiculo(s) liberado(s).'
            )
        else:
            self.message_user(
                request,
                'No se cancelaron ventas. Solo se pueden cancelar ventas ACTIVAS.',
                level='warning'
            )
    
    cancelar_ventas_seleccionadas.short_description = "Cancelar ventas seleccionadas"
    
    def save_model(self, request, obj, form, change):
        # Guardar primero sin calcular total
        if not change:
            obj.total_venta = 0
        super().save_model(request, obj, form, change)
    
    def save_formset(self, request, form, formset, change):
        # Guardar los detalles
        instances = formset.save(commit=False)
        for instance in instances:
            # Calcular precio y subtotal desde el vehiculo
            if instance.vehiculo:
                instance.precio_unitario = instance.vehiculo.precio
                instance.subtotal = instance.cantidad * instance.precio_unitario
            instance.save()
        formset.save_m2m()
        
        # Recalcular total de la venta
        venta = form.instance
        total = sum(d.subtotal for d in venta.detalles.all())
        venta.total_venta = total - venta.descuento_aplicado
        venta.save()


@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ['id', 'venta', 'vehiculo', 'cantidad', 'precio_unitario', 'subtotal']
    list_filter = ['venta__fecha_venta']
    search_fields = ['venta__id', 'vehiculo__modelo']
    readonly_fields = ['fecha_creacion']


# Personalizar el sitio admin
admin.site.site_header = 'Administración - Agencia de Autos'
admin.site.site_title = 'Agencia de Autos'
admin.site.index_title = 'Panel de Administración'


# Vistas personalizadas para reportes de procedimientos almacenados
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db import connection

@staff_member_required
def top_marcas_view(request):
    """Vista para mostrar Top Marcas y Modelos (Procedimiento: top_marcas_modelos)"""
    anio = request.GET.get('anio', None)
    limite = request.GET.get('limite', 10)
    
    with connection.cursor() as cursor:
        if anio:
            cursor.execute("SELECT * FROM top_marcas_modelos(%s, %s)", [int(anio), int(limite)])
        else:
            cursor.execute("SELECT * FROM top_marcas_modelos(NULL, %s)", [int(limite)])
        
        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    # Obtener años disponibles
    with connection.cursor() as cursor:
        cursor.execute("SELECT DISTINCT EXTRACT(YEAR FROM fecha_venta)::INT as anio FROM venta ORDER BY anio DESC")
        anios_disponibles = [row[0] for row in cursor.fetchall()]
    
    context = {
        'title': 'Top Marcas y Modelos Más Vendidos',
        'results': results,
        'anio_seleccionado': anio,
        'limite': limite,
        'anios_disponibles': anios_disponibles,
        'site_header': admin.site.site_header,
        'site_title': admin.site.site_title,
    }
    
    return render(request, 'admin/reportes/top_marcas.html', context)


@staff_member_required
def disponibilidad_view(request):
    """Vista para mostrar Disponibilidad por Marca y Tipo (Procedimiento: disponibilidad_por_marca_tipo)"""
    marca_id = request.GET.get('marca', None)
    tipo_id = request.GET.get('tipo', None)
    solo_disponibles = request.GET.get('solo_disponibles', 'true') == 'true'
    
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM disponibilidad_por_marca_tipo(%s, %s, %s)",
            [marca_id if marca_id else None, tipo_id if tipo_id else None, solo_disponibles]
        )
        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    # Obtener marcas y tipos para filtros
    from .models import Marca, TipoVehiculo
    marcas = Marca.objects.filter(activo=True).order_by('nombre')
    tipos = TipoVehiculo.objects.filter(activo=True).order_by('nombre')
    
    context = {
        'title': 'Disponibilidad de Vehículos por Marca y Tipo',
        'results': results,
        'marcas': marcas,
        'tipos': tipos,
        'marca_seleccionada': int(marca_id) if marca_id else None,
        'tipo_seleccionado': int(tipo_id) if tipo_id else None,
        'solo_disponibles': solo_disponibles,
        'site_header': admin.site.site_header,
        'site_title': admin.site.site_title,
    }
    
    return render(request, 'admin/reportes/disponibilidad.html', context)


@staff_member_required
def clasificacion_clientes_view(request):
    """Vista para mostrar Clasificación de Clientes (Procedimiento: clasificar_clientes)"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                c.id::bigint AS cliente_id,
                c.nombre_completo::varchar AS nombre_completo,
                c.email::varchar AS email,
                COUNT(v.id)::bigint AS total_compras,
                COALESCE(SUM(v.total_venta), 0)::numeric AS monto_total,
                CASE 
                    WHEN COUNT(v.id) >= 5 THEN 'VIP'
                    WHEN COUNT(v.id) >= 3 THEN 'FRECUENTE'
                    WHEN COUNT(v.id) >= 1 THEN 'REGULAR'
                    ELSE 'NUEVO'
                END AS clasificacion
            FROM cliente c
            LEFT JOIN venta v ON c.id = v.cliente_id AND v.estado_venta = 'ACTIVA'
            GROUP BY c.id, c.nombre_completo, c.email
            ORDER BY total_compras DESC, monto_total DESC
        """)
        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    # Calcular estadísticas
    vip = sum(1 for r in results if r['clasificacion'] == 'VIP')
    frecuente = sum(1 for r in results if r['clasificacion'] == 'FRECUENTE')
    regular = sum(1 for r in results if r['clasificacion'] == 'REGULAR')
    nuevo = sum(1 for r in results if r['clasificacion'] == 'NUEVO')
    
    context = {
        'title': 'Clasificación de Clientes por Frecuencia',
        'results': results,
        'stats': {
            'vip': vip,
            'frecuente': frecuente,
            'regular': regular,
            'nuevo': nuevo,
            'total': len(results)
        },
        'site_header': admin.site.site_header,
        'site_title': admin.site.site_title,
    }
    
    return render(request, 'admin/reportes/clasificacion_clientes.html', context)


@staff_member_required
def pivot_ventas_view(request):
    """Vista para mostrar PIVOT de Ventas por Mes y Marca (Vista: vw_ventas_mes_marca)"""
    anio = request.GET.get('anio', None)
    
    with connection.cursor() as cursor:
        if anio:
            cursor.execute("SELECT * FROM obtener_ventas_pivot(%s)", [int(anio)])
        else:
            cursor.execute("SELECT * FROM vw_ventas_mes_marca ORDER BY anio DESC, mes DESC LIMIT 12")
        
        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    # Obtener años disponibles
    with connection.cursor() as cursor:
        cursor.execute("SELECT DISTINCT anio FROM vw_ventas_mes_marca ORDER BY anio DESC")
        anios_disponibles = [row[0] for row in cursor.fetchall()]
    
    context = {
        'title': 'Reporte PIVOT - Ventas por Mes y Marca',
        'results': results,
        'anio_seleccionado': anio,
        'anios_disponibles': anios_disponibles,
        'site_header': admin.site.site_header,
        'site_title': admin.site.site_title,
    }
    
    return render(request, 'admin/reportes/pivot_ventas.html', context)


@staff_member_required
def ranking_marcas_view(request):
    """Vista para mostrar RANKING de Marcas (Vista: vw_top_marcas_anio)"""
    anio = request.GET.get('anio', None)
    
    with connection.cursor() as cursor:
        if anio:
            cursor.execute("SELECT * FROM obtener_top5_marcas(%s)", [int(anio)])
        else:
            cursor.execute("SELECT * FROM vw_top5_marcas ORDER BY anio DESC, posicion ASC")
        
        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    # Obtener años disponibles
    with connection.cursor() as cursor:
        cursor.execute("SELECT DISTINCT anio FROM vw_top_marcas_anio ORDER BY anio DESC")
        anios_disponibles = [row[0] for row in cursor.fetchall()]
    
    context = {
        'title': 'RANKING - Top 5 Marcas Más Vendidas',
        'results': results,
        'anio_seleccionado': anio,
        'anios_disponibles': anios_disponibles,
        'site_header': admin.site.site_header,
        'site_title': admin.site.site_title,
    }
    
    return render(request, 'admin/reportes/ranking_marcas.html', context)


@staff_member_required
def inventario_analisis_view(request):
    """Vista para mostrar Análisis de Inventario con Subconsultas (Vista: vw_inventario_analisis)"""
    estado = request.GET.get('estado', None)
    nivel = request.GET.get('nivel', None)
    
    with connection.cursor() as cursor:
        query = "SELECT * FROM vw_inventario_analisis WHERE 1=1"
        params = []
        
        if estado:
            query += " AND estado_disponibilidad = %s"
            params.append(estado)
        
        if nivel:
            query += " AND nivel_inventario = %s"
            params.append(nivel)
        
        query += " ORDER BY dias_en_inventario DESC LIMIT 50"
        
        cursor.execute(query, params)
        columns = [col[0] for col in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    context = {
        'title': 'Análisis de Inventario con Subconsultas',
        'results': results,
        'estado_seleccionado': estado,
        'nivel_seleccionado': nivel,
        'estados': ['DISPONIBLE', 'VENDIDO', 'RESERVADO'],
        'niveles': ['NUEVO', 'MEDIO', 'ALTO', 'CRITICO'],
        'site_header': admin.site.site_header,
        'site_title': admin.site.site_title,
    }
    
    return render(request, 'admin/reportes/inventario_analisis.html', context)



# Administración de tablas de auditoría

@admin.register(AudVenta)
class AudVentaAdmin(admin.ModelAdmin):
    list_display = ['id', 'venta_id', 'accion', 'usuario_bd', 'fecha_evento']
    list_filter = ['accion', 'fecha_evento']
    search_fields = ['venta_id', 'usuario_bd']
    readonly_fields = ['id', 'venta_id', 'accion', 'usuario_bd', 'fecha_evento', 
                       'old_data', 'new_data']
    date_hierarchy = 'fecha_evento'
    
    def has_add_permission(self, request):
        # No permitir agregar registros manualmente
        return False
    
    def has_delete_permission(self, request, obj=None):
        # No permitir eliminar registros de auditoría
        return False
    
    fieldsets = (
        ('Información de Auditoría', {
            'fields': ('id', 'venta_id', 'accion', 'usuario_bd', 'fecha_evento')
        }),
        ('Datos Anteriores (JSON)', {
            'fields': ('old_data',),
            'classes': ('collapse',)
        }),
        ('Datos Nuevos (JSON)', {
            'fields': ('new_data',),
            'classes': ('collapse',)
        }),
    )


@admin.register(AudVehiculo)
class AudVehiculoAdmin(admin.ModelAdmin):
    list_display = ['id', 'vehiculo_id', 'accion', 'usuario_bd', 'fecha_evento']
    list_filter = ['accion', 'fecha_evento']
    search_fields = ['vehiculo_id', 'usuario_bd']
    readonly_fields = ['id', 'vehiculo_id', 'accion', 'usuario_bd', 'fecha_evento', 
                       'old_data', 'new_data']
    date_hierarchy = 'fecha_evento'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    fieldsets = (
        ('Información de Auditoría', {
            'fields': ('id', 'vehiculo_id', 'accion', 'usuario_bd', 'fecha_evento')
        }),
        ('Datos Anteriores (JSON)', {
            'fields': ('old_data',),
            'classes': ('collapse',)
        }),
        ('Datos Nuevos (JSON)', {
            'fields': ('new_data',),
            'classes': ('collapse',)
        }),
    )


@admin.register(AudErrores)
class AudErroresAdmin(admin.ModelAdmin):
    list_display = ['id', 'origen', 'usuario_bd', 'fecha_evento', 'sqlstate']
    list_filter = ['origen', 'fecha_evento']
    search_fields = ['origen', 'detalle', 'sqlerrm', 'usuario_bd']
    readonly_fields = ['id', 'origen', 'detalle', 'sqlstate', 'sqlerrm', 
                       'usuario_bd', 'fecha_evento', 'contexto']
    date_hierarchy = 'fecha_evento'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    fieldsets = (
        ('Información del Error', {
            'fields': ('id', 'origen', 'usuario_bd', 'fecha_evento')
        }),
        ('Detalles del Error', {
            'fields': ('sqlstate', 'sqlerrm', 'detalle')
        }),
        ('Contexto (JSON)', {
            'fields': ('contexto',),
            'classes': ('collapse',)
        }),
    )


# Administrador para la sección de Reportes
from .models import Reporte

@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    """Admin para la sección de Reportes"""
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def changelist_view(self, request, extra_context=None):
        """Vista personalizada que muestra la lista de reportes"""
        from django.shortcuts import render
        
        reportes = [
            {
                'nombre': 'Top Marcas y Modelos',
                'url': '/admin/reportes/top-marcas/',
                'descripcion': 'Procedimiento: top_marcas_modelos()',
                'tecnicas': 'JOINs, GROUP BY, ORDER BY',
                'color': 'blue'
            },
            {
                'nombre': 'Disponibilidad de Vehículos',
                'url': '/admin/reportes/disponibilidad/',
                'descripcion': 'Procedimiento: disponibilidad_por_marca_tipo()',
                'tecnicas': 'Filtros dinámicos, JOINs',
                'color': 'green'
            },
            {
                'nombre': 'Clasificación de Clientes',
                'url': '/admin/reportes/clasificacion-clientes/',
                'descripcion': 'Procedimiento: clasificar_clientes()',
                'tecnicas': 'CASE, LEFT JOIN, GROUP BY',
                'color': 'orange'
            },
            {
                'nombre': 'PIVOT - Ventas por Mes',
                'url': '/admin/reportes/pivot-ventas/',
                'descripcion': 'Vista: vw_ventas_mes_marca',
                'tecnicas': 'PIVOT con SUM(CASE...)',
                'color': 'purple'
            },
            {
                'nombre': 'RANKING - Top 5 Marcas',
                'url': '/admin/reportes/ranking-marcas/',
                'descripcion': 'Vista: vw_top_marcas_anio',
                'tecnicas': 'RANK(), DENSE_RANK(), ROW_NUMBER()',
                'color': 'pink'
            },
            {
                'nombre': 'Análisis de Inventario',
                'url': '/admin/reportes/inventario-analisis/',
                'descripcion': 'Vista: vw_inventario_analisis',
                'tecnicas': 'Subconsultas, CASE, Comparaciones',
                'color': 'teal'
            },
        ]
        
        context = {
            'title': 'Reportes del Sistema',
            'reportes': reportes,
            'site_header': admin.site.site_header,
            'site_title': admin.site.site_title,
            'has_permission': True,
        }
        
        return render(request, 'admin/reportes/lista_reportes.html', context)
