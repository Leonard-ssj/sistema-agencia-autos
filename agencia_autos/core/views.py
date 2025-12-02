from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import DatabaseError
from django.db import models
from .models import Vehiculo, Cliente, Empleado, MetodoPago, Venta, Marca, TipoVehiculo
from .services.ventas import registrar_venta_service, cancelar_venta_service
from .services.reportes import ventas_por_mes_marca, top5_marcas, obtener_disponibilidad_por_marca_tipo
from .decorators import admin_required, vendedor_or_admin_required, active_employee_required


def home(request):
    """Vista principal del sistema"""
    context = {
        'total_vehiculos_disponibles': Vehiculo.objects.filter(estado_disponibilidad='DISPONIBLE').count(),
        'total_clientes': Cliente.objects.count(),
        'total_ventas_activas': Venta.objects.filter(estado_venta='ACTIVA').count(),
    }
    return render(request, 'home.html', context)


@login_required
@vendedor_or_admin_required
def lista_vehiculos(request):
    """Lista de vehículos con filtros - Vendedores y Administradores"""
    from django.core.paginator import Paginator
    from django.db.models import Avg
    
    # Ordenar por ID (del más antiguo al más reciente)
    vehiculos = Vehiculo.objects.select_related('marca', 'tipo_vehiculo').all().order_by('id')
    
    # Filtros
    marca_id = request.GET.get('marca')
    tipo_id = request.GET.get('tipo')
    estado = request.GET.get('estado')
    
    if marca_id:
        vehiculos = vehiculos.filter(marca_id=marca_id)
    if tipo_id:
        vehiculos = vehiculos.filter(tipo_vehiculo_id=tipo_id)
    if estado:
        vehiculos = vehiculos.filter(estado_disponibilidad=estado)
    
    # Calcular métricas
    total_vehiculos = Vehiculo.objects.count()
    disponibles = Vehiculo.objects.filter(estado_disponibilidad='DISPONIBLE').count()
    precio_promedio = Vehiculo.objects.aggregate(promedio=Avg('precio'))['promedio'] or 0
    
    # Paginación
    paginator = Paginator(vehiculos, 20)  # 20 vehículos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'vehiculos': page_obj,
        'page_obj': page_obj,
        'marcas': Marca.objects.filter(activo=True),
        'tipos': TipoVehiculo.objects.filter(activo=True),
        'marca_seleccionada': marca_id,
        'tipo_seleccionado': tipo_id,
        'estado_seleccionado': estado,
        'total_vehiculos': total_vehiculos,
        'disponibles': disponibles,
        'precio_promedio': precio_promedio,
    }
    return render(request, 'vehiculos/lista.html', context)


@login_required
def detalle_vehiculo(request, vehiculo_id):
    """Detalle de un vehículo específico"""
    vehiculo = get_object_or_404(
        Vehiculo.objects.select_related('marca', 'tipo_vehiculo'),
        id=vehiculo_id
    )
    return render(request, 'vehiculos/detalle.html', {'vehiculo': vehiculo})


@login_required
@vendedor_or_admin_required
def nueva_venta(request):
    """Formulario para registrar una nueva venta - Vendedores y Administradores"""
    if request.method == 'POST':
        try:
            # Obtener datos del formulario
            cliente_id = request.POST.get('cliente_id')
            empleado_id = request.POST.get('empleado_id')
            metodo_pago_id = request.POST.get('metodo_pago_id')
            vehiculo_id = request.POST.get('vehiculo_id')
            precio = request.POST.get('precio')
            descuento_temporada = request.POST.get('descuento_temporada') == 'on'
            cliente_frecuente = request.POST.get('cliente_frecuente') == 'on'
            
            # Llamar al servicio que usa SQL directo
            venta_id = registrar_venta_service(
                cliente_id=cliente_id,
                empleado_id=empleado_id,
                metodo_pago_id=metodo_pago_id,
                vehiculo_id=vehiculo_id,
                precio=precio,
                cantidad=1,
                descuento_temporada=descuento_temporada,
                cliente_frecuente=cliente_frecuente
            )
            
            messages.success(request, f'Venta #{venta_id} registrada exitosamente')
            return redirect('venta_detalle', venta_id=venta_id)
            
        except DatabaseError as e:
            messages.error(request, f'Error al registrar venta: {str(e)}')
    
    # GET - Mostrar formulario
    context = {
        'clientes': Cliente.objects.all().order_by('nombre_completo'),
        'empleados': Empleado.objects.filter(estado='ACTIVO').order_by('nombre_completo'),
        'metodos_pago': MetodoPago.objects.filter(activo=True),
        'vehiculos_disponibles': Vehiculo.objects.filter(
            estado_disponibilidad='DISPONIBLE'
        ).select_related('marca', 'tipo_vehiculo').order_by('marca__nombre', 'modelo'),
    }
    return render(request, 'ventas/nueva.html', context)


@login_required
def detalle_venta(request, venta_id):
    """Detalle de una venta específica"""
    venta = get_object_or_404(
        Venta.objects.select_related('cliente', 'empleado', 'metodo_pago'),
        id=venta_id
    )
    detalles = venta.detalles.select_related('vehiculo__marca', 'vehiculo__tipo_vehiculo').all()
    
    context = {
        'venta': venta,
        'detalles': detalles,
    }
    return render(request, 'ventas/detalle.html', context)


@login_required
@admin_required
def cancelar_venta(request, venta_id):
    """Cancelar una venta (solo administradores)"""
    # Ya no necesitamos verificar manualmente, el decorador lo hace
    
    venta = get_object_or_404(Venta, id=venta_id)
    
    if request.method == 'POST':
        try:
            # Llamar al servicio que usa SQL directo
            success = cancelar_venta_service(venta_id)
            
            if success:
                messages.success(request, f'Venta #{venta_id} cancelada exitosamente')
                return redirect('venta_detalle', venta_id=venta_id)
            else:
                messages.error(request, 'No se pudo cancelar la venta')
                
        except DatabaseError as e:
            messages.error(request, f'Error al cancelar venta: {str(e)}')
    
    return render(request, 'ventas/cancelar.html', {'venta': venta})


@login_required
def lista_ventas(request):
    """Lista de todas las ventas"""
    from django.core.paginator import Paginator
    from django.db.models import Sum, Avg
    from datetime import datetime
    
    ventas = Venta.objects.select_related(
        'cliente', 'empleado', 'metodo_pago'
    ).order_by('-fecha_creacion')
    
    # Filtro por estado
    estado = request.GET.get('estado')
    if estado:
        ventas = ventas.filter(estado_venta=estado)
    
    # Calcular métricas
    total_ventas = Venta.objects.count()
    
    # Ventas del mes actual
    mes_actual = datetime.now().month
    anio_actual = datetime.now().year
    ventas_mes = Venta.objects.filter(
        fecha_venta__month=mes_actual,
        fecha_venta__year=anio_actual,
        estado_venta='ACTIVA'
    ).count()
    
    # Ingresos del mes actual
    ingresos_mes = Venta.objects.filter(
        fecha_venta__month=mes_actual,
        fecha_venta__year=anio_actual,
        estado_venta='ACTIVA'
    ).aggregate(total=Sum('total_venta'))['total'] or 0
    
    # Promedio por venta (solo ventas activas)
    promedio_venta = Venta.objects.filter(
        estado_venta='ACTIVA'
    ).aggregate(promedio=Avg('total_venta'))['promedio'] or 0
    
    # Paginación
    paginator = Paginator(ventas, 15)  # 15 ventas por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'ventas': page_obj,
        'page_obj': page_obj,
        'estado_seleccionado': estado,
        'total_ventas': total_ventas,
        'ventas_mes': ventas_mes,
        'ingresos_mes': ingresos_mes,
        'promedio_venta': promedio_venta,
    }
    return render(request, 'ventas/lista.html', context)


@login_required
@admin_required
def reporte_ventas_mes_marca(request):
    """Reporte PIVOT de ventas por mes y marca - Solo administradores"""
    anio = request.GET.get('anio', 2024)
    
    try:
        # Llamar al servicio que consulta la vista SQL
        datos = ventas_por_mes_marca(anio)
        
        context = {
            'datos': datos,
            'anio': anio,
        }
        return render(request, 'reportes/ventas_mes_marca.html', context)
        
    except DatabaseError as e:
        messages.error(request, f'Error al generar reporte: {str(e)}')
        return redirect('home')


@login_required
@admin_required
def reporte_top5_marcas(request):
    """Reporte Top 5 marcas con RANK() - Solo administradores"""
    anio = request.GET.get('anio', 2024)
    
    try:
        # Llamar al servicio que consulta la vista SQL
        datos = top5_marcas(anio)
        
        context = {
            'datos': datos,
            'anio': anio,
        }
        return render(request, 'reportes/top5_marcas.html', context)
        
    except DatabaseError as e:
        messages.error(request, f'Error al generar reporte: {str(e)}')
        return redirect('home')


@login_required
@admin_required
def reporte_disponibilidad(request):
    """Reporte de disponibilidad de vehículos por marca y tipo - Solo administradores"""
    from django.core.paginator import Paginator
    
    try:
        # Obtener filtros
        fecha_desde = request.GET.get('fecha_desde')
        fecha_hasta = request.GET.get('fecha_hasta')
        marca_filtro = request.GET.get('marca')
        tipo_filtro = request.GET.get('tipo')
        formato = request.GET.get('formato')  # 'excel' o 'pdf'
        
        # Obtener datos con filtros
        datos = obtener_disponibilidad_por_marca_tipo(
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            marca=marca_filtro,
            tipo=tipo_filtro
        )
        
        # Si se solicita exportación
        if formato == 'excel':
            from .services.export_excel import exportar_disponibilidad_excel
            filtros = {
                'fecha_desde': fecha_desde,
                'fecha_hasta': fecha_hasta,
                'marca': marca_filtro,
                'tipo': tipo_filtro
            }
            return exportar_disponibilidad_excel(datos, filtros)
        
        elif formato == 'pdf':
            from .services.export_pdf import exportar_disponibilidad_pdf
            filtros = {
                'fecha_desde': fecha_desde,
                'fecha_hasta': fecha_hasta,
                'marca': marca_filtro,
                'tipo': tipo_filtro
            }
            return exportar_disponibilidad_pdf(datos, filtros)
        
        # Paginación
        paginator = Paginator(datos, 20)  # 20 registros por página
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Calcular métricas
        total_disponibles = sum(d['cantidad_disponible'] for d in datos)
        marcas_unicas = len(set(d['marca'] for d in datos))
        precio_promedio = sum(float(d['precio_promedio']) for d in datos) / len(datos) if datos else 0
        
        # Obtener listas únicas para filtros
        marcas_disponibles = sorted(set(d['marca'] for d in datos))
        tipos_disponibles = sorted(set(d['tipo_vehiculo'] for d in datos))
        
        context = {
            'page_obj': page_obj,
            'datos': page_obj.object_list,
            'total_disponibles': total_disponibles,
            'total_marcas': marcas_unicas,
            'precio_promedio': precio_promedio,
            'marcas_disponibles': marcas_disponibles,
            'tipos_disponibles': tipos_disponibles,
            # Mantener filtros en el contexto
            'fecha_desde': fecha_desde,
            'fecha_hasta': fecha_hasta,
            'marca_filtro': marca_filtro,
            'tipo_filtro': tipo_filtro,
        }
        return render(request, 'reportes/disponibilidad.html', context)
        
    except DatabaseError as e:
        messages.error(request, f'Error al generar reporte: {str(e)}')
        return redirect('home')


@login_required
def dashboard(request):
    """
    Dashboard diferenciado por rol
    - Administrador: Ve estadísticas completas del sistema
    - Vendedor: Ve solo sus estadísticas personales
    """
    from datetime import datetime
    from django.db.models import Sum, Count
    
    # Detectar si el usuario es administrador
    es_admin = request.user.groups.filter(name='Administrador').exists()
    
    if es_admin:
        # ========== DASHBOARD ADMINISTRADOR ==========
        
        # Estadísticas generales
        vehiculos_disponibles = Vehiculo.objects.filter(estado_disponibilidad='DISPONIBLE').count()
        
        # Ventas del mes actual
        mes_actual = datetime.now().month
        anio_actual = datetime.now().year
        ventas_mes = Venta.objects.filter(
            fecha_venta__month=mes_actual,
            fecha_venta__year=anio_actual,
            estado_venta='ACTIVA'
        ).count()
        
        # Ingresos del mes actual
        ingresos_mes = Venta.objects.filter(
            fecha_venta__month=mes_actual,
            fecha_venta__year=anio_actual,
            estado_venta='ACTIVA'
        ).aggregate(total=Sum('total_venta'))['total'] or 0
        
        # Empleados activos
        empleados_activos = Empleado.objects.filter(estado='ACTIVO').count()
        
        # Ventas recientes (últimas 5)
        ventas_recientes = Venta.objects.select_related(
            'cliente', 'empleado', 'metodo_pago'
        ).order_by('-fecha_creacion')[:5]
        
        # Alertas (vehículos con más de 90 días sin vender)
        from datetime import timedelta
        fecha_limite = datetime.now() - timedelta(days=90)
        vehiculos_antiguos = Vehiculo.objects.filter(
            estado_disponibilidad='DISPONIBLE',
            fecha_ingreso__lt=fecha_limite
        ).count()
        
        alertas = []
        if vehiculos_antiguos > 0:
            alertas.append(f'Hay {vehiculos_antiguos} vehículo(s) con más de 90 días sin vender')
        
        context = {
            'vehiculos_disponibles': vehiculos_disponibles,
            'ventas_mes': ventas_mes,
            'ingresos_mes': ingresos_mes,
            'empleados_activos': empleados_activos,
            'ventas_recientes': ventas_recientes,
            'alertas': alertas,
        }
        
        return render(request, 'dashboard/admin.html', context)
    
    else:
        # ========== DASHBOARD VENDEDOR ==========
        
        # Obtener el empleado asociado al usuario
        try:
            empleado = Empleado.objects.get(usuario=request.user)
        except Empleado.DoesNotExist:
            messages.error(request, 'No se encontró un empleado asociado a tu usuario')
            return redirect('home')
        
        # Ventas del vendedor en el mes actual
        mes_actual = datetime.now().month
        anio_actual = datetime.now().year
        mis_ventas_mes = Venta.objects.filter(
            empleado=empleado,
            fecha_venta__month=mes_actual,
            fecha_venta__year=anio_actual,
            estado_venta='ACTIVA'
        ).count()
        
        # Total vendido por el vendedor este mes
        mi_total_vendido = Venta.objects.filter(
            empleado=empleado,
            fecha_venta__month=mes_actual,
            fecha_venta__year=anio_actual,
            estado_venta='ACTIVA'
        ).aggregate(total=Sum('total_venta'))['total'] or 0
        
        # Ranking del vendedor (por número de ventas este mes)
        # Obtener todos los vendedores activos con su conteo de ventas
        vendedores_ranking = Empleado.objects.filter(
            estado='ACTIVO'
        ).annotate(
            num_ventas=Count('venta', filter=models.Q(
                venta__fecha_venta__month=mes_actual,
                venta__fecha_venta__year=anio_actual,
                venta__estado_venta='ACTIVA'
            ))
        ).order_by('-num_ventas')
        
        mi_ranking = 1
        total_vendedores = vendedores_ranking.count()
        for idx, vendedor in enumerate(vendedores_ranking, 1):
            if vendedor.id == empleado.id:
                mi_ranking = idx
                break
        
        # Mis ventas recientes (últimas 5)
        mis_ventas_recientes = Venta.objects.filter(
            empleado=empleado
        ).select_related(
            'cliente', 'metodo_pago'
        ).order_by('-fecha_creacion')[:5]
        
        context = {
            'mis_ventas_mes': mis_ventas_mes,
            'mi_total_vendido': mi_total_vendido,
            'mi_ranking': mi_ranking,
            'total_vendedores': total_vendedores,
            'mis_ventas_recientes': mis_ventas_recientes,
        }
        
        return render(request, 'dashboard/vendedor.html', context)


# Gestión de empleados

@login_required
@admin_required
def lista_empleados(request):
    """
    Lista de empleados - Solo para administradores
    Muestra todos los empleados con opción de filtrar por estado
    """
    from django.core.paginator import Paginator
    
    # Filtros
    estado_filtro = request.GET.get('estado', '')
    
    # Ordenar por ID (del más antiguo al más reciente)
    empleados = Empleado.objects.all().order_by('id')
    
    if estado_filtro:
        empleados = empleados.filter(estado=estado_filtro)
    
    # Calcular estadísticas
    total_empleados = Empleado.objects.count()
    empleados_activos = Empleado.objects.filter(estado='ACTIVO').count()
    empleados_inactivos = Empleado.objects.filter(estado='INACTIVO').count()
    
    # Paginación
    paginator = Paginator(empleados, 15)  # 15 empleados por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'empleados': page_obj,
        'page_obj': page_obj,
        'estado_filtro': estado_filtro,
        'total_empleados': total_empleados,
        'empleados_activos': empleados_activos,
        'empleados_inactivos': empleados_inactivos,
    }
    
    return render(request, 'empleados/lista.html', context)


@login_required
@admin_required
def nuevo_empleado(request):
    """
    Crear nuevo empleado - Solo para administradores
    Crea el empleado Y su usuario de Django automáticamente
    """
    # Ya no necesitamos verificar manualmente, el decorador lo hace
    
    if request.method == 'POST':
        # Obtener datos del formulario
        nombre_completo = request.POST.get('nombre_completo')
        puesto = request.POST.get('puesto')
        usuario_nombre = request.POST.get('usuario')
        contrasena = request.POST.get('contrasena')
        fecha_ingreso = request.POST.get('fecha_ingreso')
        
        try:
            # Crear usuario de Django
            from django.contrib.auth.models import User, Group
            
            # Verificar que el usuario no exista
            if User.objects.filter(username=usuario_nombre).exists():
                messages.error(request, f'El usuario "{usuario_nombre}" ya existe')
                return render(request, 'empleados/nuevo.html')
            
            # Crear usuario
            user = User.objects.create_user(
                username=usuario_nombre,
                password=contrasena,
                first_name=nombre_completo.split()[0] if nombre_completo else '',
                last_name=' '.join(nombre_completo.split()[1:]) if len(nombre_completo.split()) > 1 else ''
            )
            
            # Asignar al grupo Vendedor
            vendedor_group = Group.objects.get(name='Vendedor')
            user.groups.add(vendedor_group)
            
            # Crear empleado (usando SQL directo porque el modelo tiene managed=False)
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO empleado (nombre_completo, puesto, usuario, contrasena, fecha_ingreso, estado)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, [nombre_completo, puesto, usuario_nombre, contrasena, fecha_ingreso, 'ACTIVO'])
            
            messages.success(request, f'Empleado "{nombre_completo}" creado exitosamente')
            return redirect('empleado_lista')
            
        except Exception as e:
            messages.error(request, f'Error al crear empleado: {str(e)}')
    
    return render(request, 'empleados/nuevo.html')


@login_required
@admin_required
def editar_empleado(request, empleado_id):
    """
    Editar empleado - Solo para administradores
    Permite modificar nombre, puesto y estado del empleado
    """
    # Ya no necesitamos verificar manualmente, el decorador lo hace
    
    empleado = get_object_or_404(Empleado, id=empleado_id)
    
    if request.method == 'POST':
        # Obtener datos del formulario
        nombre_completo = request.POST.get('nombre_completo')
        puesto = request.POST.get('puesto')
        estado = request.POST.get('estado')
        
        try:
            # Actualizar empleado (usando SQL directo)
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE empleado 
                    SET nombre_completo = %s, puesto = %s, estado = %s, fecha_modificacion = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, [nombre_completo, puesto, estado, empleado_id])
            
            # Actualizar usuario de Django si existe
            from django.contrib.auth.models import User
            try:
                user = User.objects.get(username=empleado.usuario)
                user.first_name = nombre_completo.split()[0] if nombre_completo else ''
                user.last_name = ' '.join(nombre_completo.split()[1:]) if len(nombre_completo.split()) > 1 else ''
                user.is_active = (estado == 'ACTIVO')
                user.save()
            except User.DoesNotExist:
                pass  # El usuario no existe en Django
            
            messages.success(request, f'Empleado "{nombre_completo}" actualizado exitosamente')
            return redirect('empleado_lista')
            
        except Exception as e:
            messages.error(request, f'Error al actualizar empleado: {str(e)}')
    
    context = {
        'empleado': empleado,
    }
    
    return render(request, 'empleados/editar.html', context)


# Gestión de vehículos

@login_required
@admin_required
def nuevo_vehiculo(request):
    """
    Crear nuevo vehículo - Solo para administradores
    Permite agregar vehículos al inventario
    """
    # Ya no necesitamos verificar manualmente, el decorador lo hace
    
    if request.method == 'POST':
        # Obtener datos del formulario
        marca_id = request.POST.get('marca_id')
        tipo_vehiculo_id = request.POST.get('tipo_vehiculo_id')
        modelo = request.POST.get('modelo')
        anio = request.POST.get('anio')
        color = request.POST.get('color')
        vin = request.POST.get('vin')  # Cambiado de numero_serie a vin
        precio = request.POST.get('precio')
        
        try:
            # Verificar que el VIN no exista (si se proporcionó)
            if vin and Vehiculo.objects.filter(vin=vin).exists():
                messages.error(request, f'Ya existe un vehículo con el VIN "{vin}"')
                # Mantener los datos del formulario
                context = {
                    'marcas': Marca.objects.filter(activo=True),
                    'tipos': TipoVehiculo.objects.filter(activo=True),
                    'datos': request.POST,
                }
                return render(request, 'vehiculos/nuevo.html', context)
            
            # Crear vehículo (usando SQL directo porque el modelo tiene managed=False)
            from django.db import connection
            from datetime import date
            
            with connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO vehiculo (
                        marca_id, tipo_vehiculo_id, modelo, anio, color, 
                        vin, precio, estado_disponibilidad, fecha_ingreso
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, [
                    marca_id, tipo_vehiculo_id, modelo, anio, color,
                    vin if vin else None, precio, 'DISPONIBLE', date.today()
                ])
                vehiculo_id = cursor.fetchone()[0]
            
            messages.success(request, f'Vehículo "{modelo}" agregado exitosamente al inventario')
            return redirect('detalle_vehiculo', vehiculo_id=vehiculo_id)
            
        except Exception as e:
            messages.error(request, f'Error al crear vehículo: {str(e)}')
    
    # GET - Mostrar formulario
    context = {
        'marcas': Marca.objects.filter(activo=True).order_by('nombre'),
        'tipos': TipoVehiculo.objects.filter(activo=True).order_by('nombre'),
    }
    return render(request, 'vehiculos/nuevo.html', context)


@login_required
@admin_required
def editar_vehiculo(request, vehiculo_id):
    """
    Editar vehículo - Solo para administradores
    Permite modificar datos del vehículo (precio, estado, etc.)
    """
    # Ya no necesitamos verificar manualmente, el decorador lo hace
    
    vehiculo = get_object_or_404(
        Vehiculo.objects.select_related('marca', 'tipo_vehiculo'),
        id=vehiculo_id
    )
    
    # Verificar si tiene ventas activas (para deshabilitar opciones en el template)
    from .models import DetalleVenta
    tiene_ventas_activas = DetalleVenta.objects.filter(
        vehiculo_id=vehiculo_id,
        venta__estado_venta='ACTIVA'
    ).exists()
    
    if request.method == 'POST':
        # VALIDACIÓN CRÍTICA: No permitir edición si el vehículo está VENDIDO
        if tiene_ventas_activas and vehiculo.estado_disponibilidad == 'VENDIDO':
            messages.error(
                request,
                'No se puede editar un vehiculo vendido. '
                'Primero debe cancelar la venta correspondiente.'
            )
            return redirect('detalle_vehiculo', vehiculo_id=vehiculo_id)
        
        # Obtener datos del formulario
        precio = request.POST.get('precio')
        estado_disponibilidad = request.POST.get('estado_disponibilidad')
        color = request.POST.get('color')
        
        try:
            # VALIDACIÓN: Verificar cambio de estado
            if estado_disponibilidad != vehiculo.estado_disponibilidad:
                from .models import DetalleVenta
                ventas_activas = DetalleVenta.objects.filter(
                    vehiculo_id=vehiculo_id,
                    venta__estado_venta='ACTIVA'
                ).exists()
                
                if ventas_activas and estado_disponibilidad in ['DISPONIBLE', 'RESERVADO']:
                    messages.error(
                        request, 
                        f'No se puede cambiar el estado a {estado_disponibilidad}. '
                        f'El vehículo tiene ventas activas.'
                    )
                    return redirect('vehiculo_editar', vehiculo_id=vehiculo_id)
            
            # Actualizar vehículo (usando SQL directo)
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE vehiculo 
                    SET precio = %s, 
                        estado_disponibilidad = %s,
                        color = %s,
                        fecha_modificacion = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, [precio, estado_disponibilidad, color, vehiculo_id])
            
            messages.success(request, f'Vehículo "{vehiculo.modelo}" actualizado exitosamente')
            return redirect('detalle_vehiculo', vehiculo_id=vehiculo_id)
            
        except Exception as e:
            messages.error(request, f'Error al actualizar vehículo: {str(e)}')
    
    context = {
        'vehiculo': vehiculo,
        'tiene_ventas_activas': tiene_ventas_activas,
    }
    
    return render(request, 'vehiculos/editar.html', context)


# Gestión de clientes

@login_required
@admin_required
def lista_clientes(request):
    """Lista todos los clientes - Solo administradores"""
    from django.core.paginator import Paginator
    
    clientes = Cliente.objects.all().order_by('id')
    
    # Estadísticas
    total_clientes = Cliente.objects.count()
    clientes_con_compras = Cliente.objects.filter(venta__isnull=False).distinct().count()
    clientes_sin_compras = total_clientes - clientes_con_compras
    
    # Paginación
    paginator = Paginator(clientes, 15)  # 15 clientes por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'clientes': page_obj,
        'page_obj': page_obj,
        'total_clientes': total_clientes,
        'clientes_con_compras': clientes_con_compras,
        'clientes_sin_compras': clientes_sin_compras,
    }
    return render(request, 'clientes/lista.html', context)


@login_required
@admin_required
def nuevo_cliente(request):
    """Crear un nuevo cliente - Solo administradores"""
    if request.method == 'POST':
        try:
            from django.utils import timezone
            from .models import TipoDocumento
            
            cliente = Cliente.objects.create(
                nombre_completo=request.POST['nombre_completo'],
                email=request.POST['email'],
                telefono=request.POST['telefono'],
                direccion=request.POST['direccion'],
                tipo_documento_id=request.POST['tipo_documento_id'],
                numero_documento=request.POST['numero_documento'],
                fecha_registro=timezone.now().date()
            )
            messages.success(request, f'Cliente {cliente.nombre_completo} creado exitosamente.')
            return redirect('lista_clientes')
        except Exception as e:
            messages.error(request, f'Error al crear cliente: {str(e)}')
    
    from .models import TipoDocumento
    tipos_documento = TipoDocumento.objects.filter(activo=True)
    context = {
        'tipos_documento': tipos_documento,
    }
    return render(request, 'clientes/nuevo.html', context)


@login_required
@admin_required
def editar_cliente(request, cliente_id):
    """Editar un cliente existente - Solo administradores"""
    cliente = get_object_or_404(Cliente, id=cliente_id)
    
    if request.method == 'POST':
        try:
            cliente.nombre_completo = request.POST['nombre_completo']
            cliente.email = request.POST['email']
            cliente.telefono = request.POST['telefono']
            cliente.direccion = request.POST['direccion']
            cliente.tipo_documento_id = request.POST['tipo_documento_id']
            cliente.numero_documento = request.POST['numero_documento']
            cliente.save()
            
            messages.success(request, f'Cliente {cliente.nombre_completo} actualizado exitosamente.')
            return redirect('lista_clientes')
        except Exception as e:
            messages.error(request, f'Error al actualizar cliente: {str(e)}')
    
    from .models import TipoDocumento
    tipos_documento = TipoDocumento.objects.filter(activo=True)
    context = {
        'cliente': cliente,
        'tipos_documento': tipos_documento,
    }
    return render(request, 'clientes/editar.html', context)


@login_required
def detalle_cliente(request, cliente_id):
    """Ver detalle de un cliente con su historial de compras"""
    from django.db import connection
    
    cliente = get_object_or_404(Cliente, id=cliente_id)
    
    # Obtener historial usando el procedimiento almacenado
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM historial_cliente(%s)", [cliente_id])
            columns = [col[0] for col in cursor.description]
            historial = [dict(zip(columns, row)) for row in cursor.fetchall()]
    except Exception as e:
        historial = []
        messages.error(request, f'Error al obtener historial: {str(e)}')
    
    # Obtener clasificación del cliente
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
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
                WHERE c.id = %s
                GROUP BY c.id
            """, [cliente_id])
            result = cursor.fetchone()
            if result:
                total_compras = result[0]
                monto_total = result[1]
                clasificacion = result[2]
            else:
                clasificacion = 'NUEVO'
                total_compras = 0
                monto_total = 0
    except Exception as e:
        clasificacion = 'N/A'
        total_compras = 0
        monto_total = 0
        messages.error(request, f'Error al obtener clasificación: {str(e)}')
    
    context = {
        'cliente': cliente,
        'historial': historial,
        'clasificacion': clasificacion,
        'total_compras': total_compras,
        'monto_total': monto_total,
    }
    return render(request, 'clientes/detalle.html', context)
