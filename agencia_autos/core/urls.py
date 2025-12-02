from django.urls import path
from . import views

urlpatterns = [
    # Home
    path('', views.home, name='home'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Empleados
    path('empleados/', views.lista_empleados, name='empleado_lista'),
    path('empleados/nuevo/', views.nuevo_empleado, name='empleado_nuevo'),
    path('empleados/<int:empleado_id>/editar/', views.editar_empleado, name='empleado_editar'),
    
    # Vehículos
    path('vehiculos/', views.lista_vehiculos, name='vehiculo_lista'),
    path('vehiculos/nuevo/', views.nuevo_vehiculo, name='vehiculo_nuevo'),
    path('vehiculos/<int:vehiculo_id>/', views.detalle_vehiculo, name='detalle_vehiculo'),
    path('vehiculos/<int:vehiculo_id>/editar/', views.editar_vehiculo, name='vehiculo_editar'),
    
    # Ventas
    path('ventas/', views.lista_ventas, name='venta_lista'),
    path('ventas/nueva/', views.nueva_venta, name='venta_nueva'),
    path('ventas/<int:venta_id>/', views.detalle_venta, name='venta_detalle'),
    path('ventas/<int:venta_id>/cancelar/', views.cancelar_venta, name='cancelar_venta'),
    
    # Clientes
    path('clientes/', views.lista_clientes, name='lista_clientes'),
    path('clientes/nuevo/', views.nuevo_cliente, name='nuevo_cliente'),
    path('clientes/<int:cliente_id>/', views.detalle_cliente, name='detalle_cliente'),
    path('clientes/<int:cliente_id>/editar/', views.editar_cliente, name='editar_cliente'),
    
    # Reportes
    path('reportes/ventas-mes-marca/', views.reporte_ventas_mes_marca, name='reportes_ventas_mes_marca'),
    path('reportes/top5-marcas/', views.reporte_top5_marcas, name='reportes_top5_marcas'),
    path('reportes/disponibilidad/', views.reporte_disponibilidad, name='reportes_disponibilidad'),
]
