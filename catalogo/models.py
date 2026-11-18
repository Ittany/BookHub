from django.db import models
from django.core.validators import MinValueValidator

from .validators import validar_anio_publicacion, validar_isbn


class Autor(models.Model):
    nombre = models.CharField(max_length=80)
    apellido = models.CharField(max_length=80)
    nacionalidad = models.CharField(max_length=60, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['apellido', 'nombre']
        verbose_name_plural = 'Autores'
        constraints = [
            models.UniqueConstraint(
                fields=['nombre', 'apellido'],
                name='autor_unico_por_nombre_apellido',
            ),
        ]

    def __str__(self):
        return f'{self.apellido}, {self.nombre}'

    @property
    def nombre_completo(self):
        return f'{self.nombre} {self.apellido}'


class Categoria(models.Model):
    nombre = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=70, unique=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Libro(models.Model):
    titulo = models.CharField(max_length=200)
    autor = models.ForeignKey(
        Autor,
        on_delete=models.PROTECT,
        related_name='libros',
    )
    categoria = models.ManyToManyField(
        Categoria,
        related_name='libros',
        blank=True,
    )
    isbn = models.CharField(
        max_length=17,
        unique=True,
        validators=[validar_isbn],
        help_text='10 o 13 dígitos. Puedes incluir guiones.',
    )
    anio_publicacion = models.PositiveSmallIntegerField(
        validators=[validar_anio_publicacion],
    )
    paginas = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
    )
    stock_total = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
    )
    disponibles = models.PositiveSmallIntegerField(default=1)
    sinopsis = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    fecha_alta = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha_alta']
        verbose_name_plural = 'Libros'

    def __str__(self):
        return f'{self.titulo} ({self.anio_publicacion})'