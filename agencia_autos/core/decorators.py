"""
Decoradores personalizados para control de acceso basado en roles.

Este módulo proporciona decoradores que restringen el acceso a vistas
según el rol del empleado (Administrador o Vendedor).
"""

from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps


def admin_required(view_func):
    """
    Decorador que requiere que el usuario sea Administrador activo.
    
    Uso:
        @login_required
        @admin_required
        def mi_vista(request):
            ...
    
    Si el usuario no es administrador, se redirige al dashboard con un mensaje de error.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Verificar que el usuario esté autenticado
        if not request.user.is_authenticated:
            messages.error(request, 'Debes iniciar sesión para acceder a esta página')
            return redirect('login')
        
        # Verificar que el usuario pertenezca al grupo "Administrador"
        if not request.user.groups.filter(name='Administrador').exists():
            messages.error(request, 'Solo los Administradores pueden acceder a esta página')
            return redirect('dashboard')
        
        # Si pasa todas las validaciones, ejecutar la vista
        return view_func(request, *args, **kwargs)
    
    return wrapper


def vendedor_or_admin_required(view_func):
    """
    Decorador que requiere que el usuario sea Vendedor o Administrador activo.
    
    Uso:
        @login_required
        @vendedor_or_admin_required
        def mi_vista(request):
            ...
    
    Si el usuario no tiene uno de estos roles, se redirige al dashboard con un mensaje de error.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Verificar que el usuario esté autenticado
        if not request.user.is_authenticated:
            messages.error(request, 'Debes iniciar sesión para acceder a esta página')
            return redirect('login')
        
        # Verificar que el usuario pertenezca al grupo "Vendedor" o "Administrador"
        es_vendedor = request.user.groups.filter(name='Vendedor').exists()
        es_admin = request.user.groups.filter(name='Administrador').exists()
        
        if not (es_vendedor or es_admin):
            messages.error(request, 'No tienes permisos para acceder a esta página')
            return redirect('dashboard')
        
        # Si pasa todas las validaciones, ejecutar la vista
        return view_func(request, *args, **kwargs)
    
    return wrapper


def active_employee_required(view_func):
    """
    Decorador que requiere que el usuario sea un empleado activo (cualquier rol).
    
    Uso:
        @login_required
        @active_employee_required
        def mi_vista(request):
            ...
    
    Este decorador es útil para páginas que cualquier empleado puede ver,
    pero queremos asegurarnos de que esté activo.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Verificar que el usuario esté autenticado
        if not request.user.is_authenticated:
            messages.error(request, 'Debes iniciar sesión para acceder a esta página')
            return redirect('login')
        
        # Verificar que el usuario pertenezca a algún grupo (Vendedor o Administrador)
        tiene_rol = request.user.groups.filter(name__in=['Vendedor', 'Administrador']).exists()
        
        if not tiene_rol:
            messages.error(request, 'Tu usuario no tiene un rol asignado')
            return redirect('login')
        
        # Si pasa todas las validaciones, ejecutar la vista
        return view_func(request, *args, **kwargs)
    
    return wrapper
