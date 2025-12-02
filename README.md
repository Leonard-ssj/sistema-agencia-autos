# Sistema de Gestión para Agencia de Autos

Sistema integral de base de datos para gestión de ventas de vehículos desarrollado con PostgreSQL y Django.

[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Django](https://img.shields.io/badge/Django-092E20?style=flat&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)

## Descripción

Sistema completo de gestión para agencias de venta de automóviles que demuestra el dominio de técnicas avanzadas de administración de bases de datos. Incluye gestión de clientes, vehículos, ventas, empleados y auditorías con enfoque en integridad, trazabilidad y eficiencia operacional.

## Características Principales

### Técnicas de Base de Datos Implementadas

- **Triggers Automáticos**: Validación de disponibilidad y auditoría automática
- **Transacciones Atómicas**: Procesos de venta completos con COMMIT/ROLLBACK
- **Procedimientos Almacenados**: 6 funciones para operaciones complejas
- **Tablas de Auditoría**: Registro automático en 2 tablas separadas
- **Secuencias**: Generación automática de IDs únicos
- **Técnicas Avanzadas**: PIVOT, CASE, Subconsultas, JOINs, RANKING
- **Índices Optimizados**: Únicos y compuestos para rendimiento
- **Manejo de Errores**: TRY/CATCH con registro automático

### Interfaz Web Moderna

- **Django Admin**: Panel administrativo completo
- **Interfaz Responsiva**: Diseño moderno con Tailwind CSS
- **Roles de Usuario**: Administrador y Vendedor
- **Reportes Interactivos**: Visualización de datos en tiempo real
- **Auditoría Visual**: Seguimiento de cambios desde la interfaz

## Arquitectura del Sistema

```
Sistema de Gestión de Agencia de Autos
├── Base de Datos (PostgreSQL)
│   ├── 9 Tablas principales
│   ├── 3 Tablas de auditoría
│   ├── 4 Triggers automáticos
│   ├── 6 Procedimientos almacenados
│   └── 5 Vistas especializadas
├── Backend (Django)
│   ├── Modelos ORM
│   ├── Vistas de negocio
│   ├── Servicios de reportes
│   └── Panel administrativo
└── Frontend (HTML + Tailwind CSS)
    ├── Dashboard interactivo
    ├── CRUD completo
    ├── Reportes visuales
    └── Interfaz responsiva
```

## Modelo de Datos

### Tablas Principales

| Tabla | Descripción | Campos Clave |
|-------|-------------|--------------|
| **cliente** | Información de clientes | email (único), documento (único por tipo) |
| **vehiculo** | Inventario de vehículos | marca, modelo, estado_disponibilidad |
| **venta** | Registro de ventas | cliente, empleado, total, estado |
| **detalle_venta** | Detalles de cada venta | venta, vehículo, cantidad, subtotal |
| **empleado** | Personal de la agencia | usuario (único), puesto, estado |

### Tablas de Auditoría

| Tabla | Propósito |
|-------|-----------|
| **aud_ventas** | Auditoría automática de ventas (INSERT/UPDATE/DELETE) |
| **aud_vehiculos** | Auditoría automática de vehículos (INSERT/UPDATE/DELETE) |
| **aud_errores** | Registro de errores del sistema con contexto JSON |

## Instalación y Configuración

### Prerrequisitos

- Python 3.8+
- PostgreSQL 12+
- Git

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu-usuario/sistema-agencia-autos.git
cd sistema-agencia-autos
```

### 2. Configurar Base de Datos

#### Crear Usuario y Base de Datos

```sql
-- Conectarse a PostgreSQL como superusuario
psql -U postgres

-- Crear usuario y base de datos
CREATE USER autos_user WITH PASSWORD 'autos_pass';
CREATE DATABASE agencia_autos OWNER autos_user;
GRANT ALL PRIVILEGES ON DATABASE agencia_autos TO autos_user;
```

#### Ejecutar Scripts SQL (EN ORDEN)

Los scripts deben ejecutarse en el siguiente orden para garantizar la correcta creación de la estructura:

```bash
# 1. Estructura de tablas
psql -U autos_user -d agencia_autos -f db/01-ddl.sql

# 2. Tablas de auditoría
psql -U autos_user -d agencia_autos -f db/02-audit.sql

# 3. Triggers automáticos
psql -U autos_user -d agencia_autos -f db/03-triggers.sql

# 4. Procedimientos almacenados
psql -U autos_user -d agencia_autos -f db/04-functions.sql

# 5. Vistas especializadas
psql -U autos_user -d agencia_autos -f db/05-views.sql

# 6. Datos de prueba
psql -U autos_user -d agencia_autos -f db/06-seed.sql

# 7. Permisos de usuario
psql -U autos_user -d agencia_autos -f db/07-permisos-usuario.sql
```

### 3. Configurar Django

#### Crear Entorno Virtual

```bash
cd agencia_autos
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

#### Instalar Dependencias

```bash
pip install -r requirements.txt
```

#### Configurar Variables de Entorno

Crear archivo `.env` en `agencia_autos/`:

```env
DEBUG=True
SECRET_KEY=tu-clave-secreta-aqui
DB_NAME=agencia_autos
DB_USER=autos_user
DB_PASSWORD=autos_pass
DB_HOST=localhost
DB_PORT=5432
```

#### Aplicar Migraciones y Crear Superusuario

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

#### Configurar Roles de Usuario

```bash
python setup_roles.py
```

## Funcionalidades por Criterio de Evaluación

### 1. Triggers (10%)

**Implementación:**
- `trg_check_disponibilidad`: Valida disponibilidad antes de venta
- `trg_update_estado_vehiculo`: Actualiza estado automáticamente
- `trg_audit_ventas`: Auditoría automática de ventas
- `trg_audit_vehiculos`: Auditoría automática de vehículos

**Demostración:**
```sql
-- Probar validación de disponibilidad
INSERT INTO detalle_venta (venta_id, vehiculo_id, cantidad, precio_unitario, subtotal)
VALUES (1, 999, 1, 10000, 10000); -- Error: vehículo no disponible
```

### 2. Transacciones (10%)

**Implementación:**
- `registrar_venta()`: Transacción atómica (Venta + Detalle)
- `cancelar_venta()`: Reversión automática con ROLLBACK
- Manejo de errores con TRY/CATCH

**Demostración:**
```sql
-- Registrar venta completa
SELECT registrar_venta(1, 1, 1, 5, 250000, 1, FALSE, FALSE);

-- Cancelar venta con reversión
SELECT cancelar_venta(1);
```

### 3. Procedimientos Almacenados (10%)

**Funciones Implementadas:**

| Función | Propósito | Parámetros |
|---------|-----------|------------|
| `registrar_venta()` | Crear venta con validaciones | cliente, empleado, vehículo, precio, descuentos |
| `cancelar_venta()` | Cancelar y revertir venta | venta_id |
| `historial_cliente()` | Historial de compras | cliente_id |
| `top_marcas_modelos()` | Marcas más vendidas | año, límite |
| `disponibilidad_por_marca_tipo()` | Filtrar vehículos | marca, tipo, disponible |
| `clasificar_clientes()` | Clasificación por frecuencia | - |

### 4. Tablas de Auditoría (10%)

**Características:**
- **2 Tablas Separadas**: `aud_ventas` y `aud_vehiculos`
- **Registro Automático**: INSERT, UPDATE, DELETE
- **Usuario y Fecha**: Quién y cuándo modificó
- **Datos Completos**: Valores anteriores y nuevos en JSON

### 5. Secuencias (10%)

**Implementación:**
- Todas las tablas usan `BIGSERIAL`
- IDs únicos y secuenciales automáticos
- Control de numeración garantizado

### 6. Técnicas Avanzadas (10%)

**PIVOT:**
```sql
-- Vista de ventas por mes y marca
SELECT * FROM vw_ventas_mes_marca WHERE anio = 2024;
```

**CASE:**
```sql
-- Clasificación de clientes
SELECT * FROM clasificar_clientes();
```

**RANKING:**
```sql
-- Top 5 marcas con posiciones
SELECT * FROM vw_top_marcas_anio WHERE anio = 2024;
```

### 7. Índices y Sequence (10%)

**Índices Implementados:**
- Único: `idx_cliente_email`
- Compuesto único: `idx_cliente_documento`
- Compuesto: `idx_vehiculo_marca_modelo`
- Rendimiento: `idx_venta_estado`, `idx_venta_fecha`

### 8. TRY/CATCH (10%)

**Implementación:**
- 2 bloques en procedimientos diferentes
- Registro automático en `aud_errores`
- ROLLBACK automático en errores

## Uso del Sistema

### Acceso al Sistema

1. **Interfaz Web**: http://localhost:8000/
2. **Panel Admin**: http://localhost:8000/admin/
3. **Reportes**: http://localhost:8000/admin/reportes/

### Roles de Usuario

#### Administrador
- Gestión completa de empleados
- Creación y edición de vehículos
- Cancelación de ventas
- Acceso a todos los reportes
- Visualización de auditorías

#### Vendedor
- Gestión de clientes
- Registro de ventas
- Consulta de vehículos disponibles
- Reportes básicos

### Flujo de Trabajo Típico

1. **Registro de Cliente**
   - Captura de datos personales
   - Validación de documento único
   - Clasificación automática

2. **Gestión de Inventario**
   - Alta de vehículos
   - Control de disponibilidad
   - Seguimiento de estados

3. **Proceso de Venta**
   - Selección de cliente y vehículo
   - Aplicación de descuentos
   - Registro transaccional
   - Actualización automática de estados

4. **Seguimiento y Auditoría**
   - Historial de cambios
   - Reportes de ventas
   - Análisis de inventario

## Reportes Disponibles

### Reportes Operacionales

1. **Top Marcas y Modelos**: Más vendidos por período
2. **Disponibilidad de Vehículos**: Filtros por marca y tipo
3. **Clasificación de Clientes**: VIP, Frecuente, Regular, Nuevo
4. **Historial de Cliente**: Compras y estadísticas

### Reportes Analíticos

1. **PIVOT - Ventas por Mes**: Matriz de ventas por marca
2. **RANKING - Top 5 Marcas**: Posicionamiento anual
3. **Análisis de Inventario**: Subconsultas y comparaciones
4. **Auditoría Consolidada**: Seguimiento de cambios

## Tecnologías Utilizadas

### Backend
- **PostgreSQL 14+**: Base de datos principal
- **Django 4.2**: Framework web
- **Python 3.8+**: Lenguaje de programación

### Frontend
- **HTML5**: Estructura
- **Tailwind CSS**: Estilos modernos
- **JavaScript**: Interactividad

### Herramientas
- **Git**: Control de versiones
- **pgAdmin**: Administración de BD
- **VS Code**: Editor de código

## Estructura del Proyecto

```
sistema-agencia-autos/
├── db/                          # Scripts SQL
│   ├── 01-ddl.sql              # Definición de tablas
│   ├── 02-audit.sql            # Tablas de auditoría
│   ├── 03-triggers.sql         # Triggers automáticos
│   ├── 04-functions.sql        # Procedimientos almacenados
│   ├── 05-views.sql            # Vistas especializadas
│   ├── 06-seed.sql             # Datos de prueba
│   └── 07-permisos-usuario.sql # Configuración de permisos
├── agencia_autos/              # Aplicación Django
│   ├── config/                 # Configuración del proyecto
│   ├── core/                   # Aplicación principal
│   │   ├── models.py           # Modelos ORM
│   │   ├── views.py            # Vistas de negocio
│   │   ├── admin.py            # Panel administrativo
│   │   ├── services/           # Servicios de negocio
│   │   ├── templates/          # Templates HTML
│   │   └── static/             # Archivos estáticos
│   ├── manage.py               # Comando Django
│   ├── setup_roles.py          # Configuración de roles
│   └── .env.example            # Ejemplo de variables de entorno
├── README.md                   # Este archivo
├── .gitignore                  # Archivos ignorados por Git
└── requirements.txt            # Dependencias Python
```

## Testing

### Pruebas de Base de Datos

```bash
# Conectarse a la base de datos
psql -U autos_user -d agencia_autos

# Verificar triggers
SELECT tgname, tgrelid::regclass FROM pg_trigger WHERE tgisinternal = false;

# Verificar procedimientos
\df

# Verificar vistas
\dv

# Verificar índices
\di
```

### Pruebas de Aplicación

```bash
# Ejecutar servidor de desarrollo
python manage.py runserver

# Probar conexión a BD
python test_db_connection.py

# Verificar migraciones
python manage.py showmigrations
```

## Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT.

## Autores

- **Tu Nombre** - *Desarrollo inicial*

## Agradecimientos

- Profesores del curso de Administración de Bases de Datos
- Comunidad de Django y PostgreSQL
- Documentación oficial de las tecnologías utilizadas

---

**Si este proyecto te fue útil, no olvides darle una estrella!**
