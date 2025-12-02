# Sistema de Gestión para Agencia de Autos

> Proyecto académico de Administración de Bases de Datos

Sistema de gestión para agencias de venta de automóviles desarrollado con PostgreSQL y Django, implementando técnicas avanzadas de bases de datos.

[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Django](https://img.shields.io/badge/Django-092E20?style=flat&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)

## Descripción

Proyecto escolar que demuestra la implementación de técnicas avanzadas de administración de bases de datos en un sistema real de gestión de ventas de vehículos. Incluye triggers, procedimientos almacenados, transacciones, auditorías y reportes analíticos.

## Tecnologías

- **Backend**: Django 4.2 + Python 3.8+
- **Base de Datos**: PostgreSQL 14+
- **Frontend**: HTML5 + Tailwind CSS
- **ORM**: Django ORM con consultas SQL nativas

## Estructura del Proyecto

```
sistema-agencia-autos/
├── db/                    # Scripts SQL (ejecutar en orden)
│   ├── 01-ddl.sql        # Tablas y estructura
│   ├── 02-audit.sql      # Tablas de auditoría
│   ├── 03-triggers.sql   # Triggers automáticos
│   ├── 04-functions.sql  # Procedimientos almacenados
│   ├── 05-views.sql      # Vistas especializadas
│   ├── 06-seed.sql       # Datos de prueba
│   └── 07-permisos-usuario.sql
└── agencia_autos/        # Aplicación Django
    ├── config/           # Configuración
    ├── core/             # Lógica principal
    └── manage.py
```

## Base de Datos

### Componentes Principales

- **9 Tablas**: cliente, vehiculo, venta, detalle_venta, empleado, marca, tipo_vehiculo, metodo_pago, tipo_documento
- **3 Tablas de Auditoría**: aud_ventas, aud_vehiculos, aud_errores
- **4 Triggers**: Validación de disponibilidad, actualización de estados, auditoría automática
- **6 Procedimientos Almacenados**: registrar_venta, cancelar_venta, historial_cliente, top_marcas_modelos, disponibilidad_por_marca_tipo, clasificar_clientes
- **5 Vistas**: Reportes PIVOT, RANKING, análisis de inventario

### Funcionalidades Principales

- **Gestión de Ventas**: Registro transaccional con validaciones automáticas
- **Control de Inventario**: Seguimiento de disponibilidad en tiempo real
- **Auditoría Completa**: Registro automático de todas las operaciones
- **Reportes Analíticos**: PIVOT de ventas, ranking de marcas, clasificación de clientes
- **Roles de Usuario**: Administrador y Vendedor con permisos diferenciados
- **Panel Administrativo**: Django Admin personalizado con reportes integrados


### Scripts SQL

Los scripts en la carpeta `db/` deben ejecutarse en orden:

1. **01-ddl.sql**: Crea las 9 tablas principales con índices y constraints
2. **02-audit.sql**: Crea las 3 tablas de auditoría
3. **03-triggers.sql**: Implementa los 4 triggers automáticos
4. **04-functions.sql**: Define los 6 procedimientos almacenados
5. **05-views.sql**: Crea las 5 vistas especializadas (PIVOT, RANKING, etc.)
6. **06-seed.sql**: Inserta datos de prueba
7. **07-permisos-usuario.sql**: Configura permisos de base de datos


## Notas del Proyecto

Este es un proyecto académico desarrollado para el curso de Administración de Bases de Datos. El objetivo principal es demostrar la implementación práctica de técnicas avanzadas de bases de datos en un sistema funcional.

## Autor

**Leonardo Alonso Aldana** - Proyecto Escolar de Administración de Bases de Datos
Escuela: Universidad Tecnologica de México
