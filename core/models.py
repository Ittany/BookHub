from datetime import timedelta
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

class Perfil(models.Model):
    LECTOR = 'lector'
    BIBLIOTECARIO = 'bibliotecario'
    ROLES = [(LECTOR,'Usuario / lector'), (BIBLIOTECARIO,'Bibliotecario')]
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='perfil')
    rol = models.CharField(max_length=20, choices=ROLES, default=LECTOR)
    codigo = models.CharField('Código universitario', max_length=30, blank=True)
    def __str__(self):
        return f'{self.usuario.username} · {self.get_rol_display()}'

class Autor(models.Model):
    nombre = models.CharField(max_length=140, unique=True)
    class Meta:
        ordering = ['nombre']
    def __str__(self):
        return self.nombre

class Categoria(models.Model):
    nombre = models.CharField(max_length=90, unique=True)
    class Meta:
        ordering = ['nombre']
        verbose_name_plural = 'Categorías'
    def __str__(self):
        return self.nombre

class Libro(models.Model):
    titulo = models.CharField(max_length=220)
    autor = models.ForeignKey(Autor, on_delete=models.PROTECT, related_name='libros')
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='libros')
    isbn = models.CharField(max_length=17, unique=True, help_text='ISBN único, con o sin guiones')
    editorial = models.CharField(max_length=140, blank=True)
    anio = models.PositiveSmallIntegerField('Año de publicación', null=True, blank=True)
    descripcion = models.TextField(blank=True)
    ejemplares = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    portada = models.ImageField(upload_to='portadas/', null=True, blank=True)
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['titulo']
    def __str__(self):
        return self.titulo
    @property
    def disponibles(self):
        return max(0, self.ejemplares - self.prestamos.filter(estado=Prestamo.PRESTADO).count())
    def clean(self):
        if self.pk and self.ejemplares < self.prestamos.filter(estado=Prestamo.PRESTADO).count():
            raise ValidationError({'ejemplares':'No puede reducir el stock por debajo de los préstamos activos.'})

class Prestamo(models.Model):
    SOLICITADO = 'solicitado'
    PRESTADO = 'prestado'
    DEVUELTO = 'devuelto'
    RECHAZADO = 'rechazado'
    ESTADOS = [(SOLICITADO,'Solicitado'),(PRESTADO,'Prestado'),(DEVUELTO,'Devuelto'),(RECHAZADO,'Rechazado')]
    libro = models.ForeignKey(Libro, on_delete=models.PROTECT, related_name='prestamos')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='prestamos')
    estado = models.CharField(max_length=12, choices=ESTADOS, default=SOLICITADO)
    solicitado = models.DateTimeField(auto_now_add=True)
    fecha_prestamo = models.DateTimeField(null=True, blank=True)
    fecha_limite = models.DateField(null=True, blank=True)
    fecha_devolucion = models.DateTimeField(null=True, blank=True)
    gestionado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='prestamos_gestionados')
    class Meta:
        ordering = ['-solicitado']
    def __str__(self):
        return f'{self.libro} / {self.usuario} ({self.get_estado_display()})'
    @property
    def vencido(self):
        return self.estado == self.PRESTADO and self.fecha_limite and self.fecha_limite < timezone.localdate()
