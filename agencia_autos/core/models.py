from django.db import models
from django.contrib.postgres.fields import JSONField


class Marca(models.Model):
    id = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=50, unique=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'marca'
        managed = False  # Tabla ya existe en PostgreSQL
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'

    def __str__(self):
        return self.nombre


class TipoVehiculo(models.Model):
    id = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=30, unique=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tipo_vehiculo'
        managed = False
        verbose_name = 'Tipo de Vehículo'
        verbose_name_plural = 'Tipos de Vehículo'

    def __str__(self):
        return self.nombre


class MetodoPago(models.Model):
    id = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=30, unique=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'metodo_pago'
        managed = False
        verbose_name = 'Método de Pago'
        verbose_name_plural = 'Métodos de Pago'

    def __str__(self):
        return self.nombre


class TipoDocumento(models.Model):
    id = models.BigAutoField(primary_key=True)
    nombre = models.CharField(max_length=20, unique=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tipo_documento'
        managed = False
        verbose_name = 'Tipo de Documento'
        verbose_name_plural = 'Tipos de Documento'

    def __str__(self):
        return self.nombre






class Empleado(models.Model):
    ESTADO_CHOICES = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
    ]

    id = models.BigAutoField(primary_key=True)
    nombre_completo = models.CharField(max_length=100)
    puesto = models.CharField(max_length=50)
    usuario = models.CharField(max_length=50, unique=True)
    contrasena = models.CharField(max_length=100)
    fecha_ingreso = models.DateField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='ACTIVO')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'empleado'
        managed = False
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'

    def __str__(self):
        return f"{self.nombre_completo} - {self.puesto}"
    
    @property
    def nombre(self):
        """Alias para nombre_completo (usado en templates)"""
        return self.nombre_completo












class Cliente(models.Model):
    id = models.BigAutoField(primary_key=True)
    nombre_completo = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.CharField(max_length=150, blank=True, null=True)
    tipo_documento = models.ForeignKey(TipoDocumento, on_delete=models.RESTRICT, db_column='tipo_documento_id')
    numero_documento = models.CharField(max_length=30)
    fecha_registro = models.DateField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cliente'
        managed = False
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        unique_together = [['tipo_documento', 'numero_documento']]

    def __str__(self):
        return f"{self.nombre_completo} - {self.email}"
    
    @property
    def nombre(self):
        """Retorna la primera parte del nombre completo"""
        return self.nombre_completo.split()[0] if self.nombre_completo else ''
    
    @property
    def apellido(self):
        """Retorna la segunda parte del nombre completo"""
        partes = self.nombre_completo.split()
        return ' '.join(partes[1:]) if len(partes) > 1 else ''


class Vehiculo(models.Model):
    ESTADO_CHOICES = [
        ('DISPONIBLE', 'Disponible'),
        ('VENDIDO', 'Vendido'),
        ('RESERVADO', 'Reservado'),
    ]

    id = models.BigAutoField(primary_key=True)
    marca = models.ForeignKey(Marca, on_delete=models.RESTRICT, db_column='marca_id')
    modelo = models.CharField(max_length=50)
    anio = models.IntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    color = models.CharField(max_length=30)
    tipo_vehiculo = models.ForeignKey(TipoVehiculo, on_delete=models.RESTRICT, db_column='tipo_vehiculo_id')
    vin = models.CharField(max_length=17, unique=True, blank=True, null=True)
    estado_disponibilidad = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='DISPONIBLE')
    fecha_ingreso = models.DateField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'vehiculo'
        managed = False
        verbose_name = 'Vehículo'
        verbose_name_plural = 'Vehículos'

    def __str__(self):
        return f"{self.marca.nombre} {self.modelo} {self.anio}"


class Venta(models.Model):
    ESTADO_CHOICES = [
        ('ACTIVA', 'Activa'),
        ('CANCELADA', 'Cancelada'),
        ('PENDIENTE', 'Pendiente'),
    ]

    id = models.BigAutoField(primary_key=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.RESTRICT, db_column='cliente_id')
    empleado = models.ForeignKey(Empleado, on_delete=models.RESTRICT, db_column='empleado_id')
    metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.RESTRICT, db_column='metodo_pago_id')
    fecha_venta = models.DateField()
    total_venta = models.DecimalField(max_digits=10, decimal_places=2)
    descuento_aplicado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado_venta = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='ACTIVA')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'venta'
        managed = False
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'

    def __str__(self):
        return f"Venta #{self.id} - {self.cliente.nombre_completo}"


class DetalleVenta(models.Model):
    id = models.BigAutoField(primary_key=True)
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, db_column='venta_id', related_name='detalles')
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.RESTRICT, db_column='vehiculo_id')
    cantidad = models.IntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'detalle_venta'
        managed = False
        verbose_name = 'Detalle de Venta'
        verbose_name_plural = 'Detalles de Venta'
        unique_together = [['venta', 'vehiculo']]
    
    def clean(self):
        from django.core.exceptions import ValidationError
        # Validar que el vehiculo este disponible
        if self.vehiculo and self.vehiculo.estado_disponibilidad != 'DISPONIBLE':
            raise ValidationError({
                'vehiculo': f'El vehiculo {self.vehiculo.marca.nombre} {self.vehiculo.modelo} (ID: {self.vehiculo.id}) no esta disponible. Estado actual: {self.vehiculo.estado_disponibilidad}'
            })
        
        # Calcular precio_unitario desde el vehiculo si no esta establecido
        if self.vehiculo and not self.precio_unitario:
            self.precio_unitario = self.vehiculo.precio
        
        # Calcular subtotal
        if self.precio_unitario and self.cantidad:
            self.subtotal = self.precio_unitario * self.cantidad
    
    def save(self, *args, **kwargs):
        # Calcular valores antes de guardar
        if self.vehiculo and not self.precio_unitario:
            self.precio_unitario = self.vehiculo.precio
        if self.precio_unitario and self.cantidad:
            self.subtotal = self.precio_unitario * self.cantidad
        
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Detalle Venta #{self.venta.id} - {self.vehiculo}"


# Modelos de auditoría

class AudVenta(models.Model):
    """Tabla de auditoría para ventas"""
    id = models.BigAutoField(primary_key=True)
    venta_id = models.BigIntegerField(null=True, blank=True)
    accion = models.CharField(max_length=10)  # INSERT, UPDATE, DELETE
    usuario_bd = models.CharField(max_length=100)
    fecha_evento = models.DateTimeField()
    old_data = models.JSONField(null=True, blank=True, db_column='old_data')
    new_data = models.JSONField(null=True, blank=True, db_column='new_data')

    class Meta:
        db_table = 'aud_ventas'  # Nombre correcto en plural
        managed = False
        verbose_name = 'Auditoría de Venta'
        verbose_name_plural = 'Auditorías de Ventas'
        ordering = ['-fecha_evento']

    def __str__(self):
        return f"{self.accion} - Venta #{self.venta_id} - {self.fecha_evento}"


class AudVehiculo(models.Model):
    """Tabla de auditoría para vehículos"""
    id = models.BigAutoField(primary_key=True)
    vehiculo_id = models.BigIntegerField(null=True, blank=True)
    accion = models.CharField(max_length=10)  # INSERT, UPDATE, DELETE
    usuario_bd = models.CharField(max_length=100)
    fecha_evento = models.DateTimeField()
    old_data = models.JSONField(null=True, blank=True, db_column='old_data')
    new_data = models.JSONField(null=True, blank=True, db_column='new_data')

    class Meta:
        db_table = 'aud_vehiculos'  # Nombre correcto en plural
        managed = False
        verbose_name = 'Auditoría de Vehículo'
        verbose_name_plural = 'Auditorías de Vehículos'
        ordering = ['-fecha_evento']

    def __str__(self):
        return f"{self.accion} - Vehículo #{self.vehiculo_id} - {self.fecha_evento}"


class AudErrores(models.Model):
    """Tabla de auditoría para errores del sistema"""
    id = models.BigAutoField(primary_key=True)
    origen = models.CharField(max_length=100)
    detalle = models.TextField()
    sqlstate = models.CharField(max_length=10, null=True, blank=True)
    sqlerrm = models.TextField(null=True, blank=True)
    usuario_bd = models.CharField(max_length=100)
    fecha_evento = models.DateTimeField()
    contexto = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = 'aud_errores'
        managed = False
        verbose_name = 'Error del Sistema'
        verbose_name_plural = 'Errores del Sistema'
        ordering = ['-fecha_evento']

    def __str__(self):
        return f"{self.origen} - {self.fecha_evento}"


# Modelo proxy para la sección de Reportes en el admin
class Reporte(models.Model):
    """Modelo proxy para organizar los reportes en el admin"""
    
    class Meta:
        managed = False  # No crear tabla en la BD
        verbose_name = 'Reporte'
        verbose_name_plural = 'Reportes del Sistema'
