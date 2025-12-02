# Sistema de Gestión de Agencia de Autos - Django

## ✅ Proyecto Creado con Comandos Oficiales de Django

Este proyecto fue creado usando los comandos oficiales:
- `django-admin startproject config .`
- `python manage.py startapp core`

## 📋 Requisitos Previos

- Python 3.10+
- PostgreSQL 14+
- Base de datos `agencia_autos` creada y con scripts SQL ejecutados

## 🚀 Instalación

### 1. Activar Entorno Virtual

```cmd
cd agencia_autos
.venv\Scripts\activate
```

### 2. Instalar Dependencias (si es necesario)

```cmd
pip install -r requirements.txt
```

### 3. Configurar Variables de Entorno

El archivo `.env` ya está creado con la configuración por defecto.

### 4. Verificar Conexión

```cmd
python manage.py check
```

Deberías ver:
```
System check identified no issues (0 silenced).
```

### 5. NO Ejecutar Migraciones

**IMPORTANTE:** NO ejecutes `python manage.py migrate` porque las tablas ya existen en PostgreSQL.

### 6. Crear Superusuario

```cmd
python manage.py createsuperuser
```

### 7. Ejecutar Servidor

```cmd
python manage.py runserver
```

Accede a:
- **Admin:** http://127.0.0.1:8000/admin/

## 📁 Estructura del Proyecto

```
agencia_autos/
├── config/                 # Configuración Django (creado con django-admin)
│   ├── __init__.py
│   ├── settings.py        # ✅ Configurado con PostgreSQL
│   ├── urls.py            # ✅ Incluye core.urls
│   ├── wsgi.py
│   └── asgi.py
├── core/                   # App principal (creado con startapp)
│   ├── migrations/
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ventas.py      # ✅ registrar_venta(), cancelar_venta()
│   │   └── reportes.py    # ✅ Consultas a vistas SQL
│   ├── templates/
│   ├── static/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py          # ✅ 9 modelos (mapean a tablas existentes)
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── .venv/                  # Entorno virtual
├── manage.py               # ✅ Django CLI
├── requirements.txt        # ✅ Dependencias
├── .env                    # ✅ Variables de entorno
├── .gitignore              # ✅ Git ignore
└── README.md               # ✅ Este archivo
```

## 🔧 Uso de Servicios SQL

### Registrar Venta

```python
from core.services.ventas import registrar_venta_service

venta_id = registrar_venta_service(
    cliente_id=1,
    empleado_id=1,
    metodo_pago_id=1,
    vehiculo_id=7,
    precio=425000.00,
    cantidad=1,
    descuento_temporada=True,
    cliente_frecuente=False
)
```

### Cancelar Venta

```python
from core.services.ventas import cancelar_venta_service

success = cancelar_venta_service(venta_id=25)
```

### Consultar Reportes

```python
from core.services.reportes import ventas_por_mes_marca, top5_marcas

# Reporte PIVOT
ventas = ventas_por_mes_marca(anio=2024)

# Top 5 marcas con RANK()
top_marcas = top5_marcas(anio=2024)
```

## 🎯 Próximos Pasos

1. ✅ Proyecto creado con comandos Django
2. ✅ Modelos configurados
3. ✅ Servicios SQL creados
4. ⏳ Configurar admin.py
5. ⏳ Crear vistas y templates
6. ⏳ Implementar formularios
7. ⏳ Configurar roles y permisos

## 📝 Notas Importantes

- **Proyecto creado correctamente** con `django-admin startproject`
- **App creada correctamente** con `python manage.py startapp`
- **NO usar ORM para ventas:** Usa `registrar_venta_service()` y `cancelar_venta_service()`
- **Triggers automáticos:** Se ejecutan en PostgreSQL, no en Django
- **Auditoría:** Se registra automáticamente en la BD
- **Transacciones:** Manejadas por funciones PostgreSQL

## ✅ Verificación

```cmd
python manage.py check
```

Si todo está bien, deberías ver:
```
System check identified no issues (0 silenced).
```
