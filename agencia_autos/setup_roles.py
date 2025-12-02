import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from core.models import Vehiculo, Venta, Cliente, Empleado

def crear_grupos():
    
    # Crear grupo Administrador
    admin_group, created = Group.objects.get_or_create(name='Administrador')
    if created:
        print("Grupo 'Administrador' creado")
    else:
        print("Grupo 'Administrador' ya existe")
    
    # Crear grupo Vendedor
    vendedor_group, created = Group.objects.get_or_create(name='Vendedor')
    if created:
        print("Grupo 'Vendedor' creado")
    else:
        print("Grupo 'Vendedor' ya existe")
    
    return admin_group, vendedor_group


def asignar_permisos_admin(admin_group):
    
    # Obtener todos los permisos
    all_permissions = Permission.objects.all()
    admin_group.permissions.set(all_permissions)
    
    print(f"Asignados {all_permissions.count()} permisos al grupo Administrador")


def asignar_permisos_vendedor(vendedor_group):
    
    # Como los modelos tienen managed=False, no tienen permisos automáticos
    # Los permisos se manejarán por decoradores en las vistas
    print("Permisos de Vendedor se manejan por decoradores en vistas")


def asignar_superusuario_a_admin():
    """Asignar el superusuario al grupo Administrador"""
    
    try:
        admin_user = User.objects.get(username='admin')
        admin_group = Group.objects.get(name='Administrador')
        admin_user.groups.add(admin_group)
        print(f"Usuario 'admin' agregado al grupo Administrador")
    except User.DoesNotExist:
        print("Usuario 'admin' no encontrado. Crealo con: python manage.py createsuperuser")
    except Group.DoesNotExist:
        print("Grupo 'Administrador' no encontrado")


def main():
    print("\n" + "="*60)
    print("CONFIGURACIÓN DE ROLES Y PERMISOS")
    print("="*60 + "\n")
    
    # 1. Crear grupos
    admin_group, vendedor_group = crear_grupos()
    
    # 2. Asignar permisos
    print("\nAsignando permisos...")
    asignar_permisos_admin(admin_group)
    asignar_permisos_vendedor(vendedor_group)
    
    # 3. Asignar superusuario a admin
    print("\n👤 Configurando usuarios...")
    asignar_superusuario_a_admin()
    
    print("\n" + "="*60)
    print("CONFIGURACION COMPLETADA")
    print("="*60)
    print("\nGrupos creados:")
    print("Administrador - Acceso total")
    print("Vendedor - Acceso limitado")
    print("\nPara asignar un usuario a un grupo:")
    print("  1. Ir a http://127.0.0.1:8000/admin/")
    print("  2. Usuarios → Seleccionar usuario")
    print("  3. Grupos → Seleccionar grupo")
    print("  4. Guardar")
    print()


if __name__ == '__main__':
    main()
