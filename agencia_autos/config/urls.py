"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import path, include
from core.admin import (
    top_marcas_view, disponibilidad_view, clasificacion_clientes_view,
    pivot_ventas_view, ranking_marcas_view, inventario_analisis_view
)

urlpatterns = [
    # Rutas de reportes personalizados en Admin (ANTES de admin.site.urls)
    path('admin/reportes/top-marcas/', top_marcas_view, name='admin_top_marcas'),
    path('admin/reportes/disponibilidad/', disponibilidad_view, name='admin_disponibilidad'),
    path('admin/reportes/clasificacion-clientes/', clasificacion_clientes_view, name='admin_clasificacion_clientes'),
    path('admin/reportes/pivot-ventas/', pivot_ventas_view, name='admin_pivot_ventas'),
    path('admin/reportes/ranking-marcas/', ranking_marcas_view, name='admin_ranking_marcas'),
    path('admin/reportes/inventario-analisis/', inventario_analisis_view, name='admin_inventario_analisis'),
    
    # Admin principal
    path('admin/', admin.site.urls),
    
    path('accounts/', include('django.contrib.auth.urls')),  # URLs de autenticación
    path('', include('core.urls')),
]
