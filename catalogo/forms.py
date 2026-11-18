"""
Formularios de BookHub.

Demuestra:
  - ModelForm  → LibroForm (persiste en DB)
  - Form       → BusquedaLibroForm (no persiste)
  - clean_<campo>()  → validación por campo
  - clean()          → validación cross-field
  - sanitize_input() → limpieza de entrada
"""
import re

from django import forms
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags

from .models import Autor, Categoria, Libro


# ---------------------------------------------------------------
# Sanitización reutilizable
# ---------------------------------------------------------------
def sanitize_input(value) -> str:
    """
    Limpieza básica de entrada:
      1. Quita etiquetas HTML (previene XSS almacenado)
      2. Colapsa espacios repetidos
      3. Hace strip final
    No es un WAF, pero es el primer escudo antes de tocar la DB.
    """
    if value is None:
        return ''
    value = strip_tags(str(value))
    value = re.sub(r'\s+', ' ', value)
    return value.strip()


# ---------------------------------------------------------------
# ModelForm: crea/edita libros
# ---------------------------------------------------------------
class LibroForm(forms.ModelForm):
    class Meta:
        model = Libro
        fields = [
            'titulo', 'autor', 'categoria', 'isbn',
            'anio_publicacion', 'paginas', 'stock_total',
            'disponibles', 'sinopsis', 'activo',
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título del libro'}),
            'autor': forms.Select(attrs={'class': 'form-control'}),
            'categoria': forms.SelectMultiple(attrs={'class': 'form-control', 'size': 4}),
            'isbn': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '978-84-376-0494-7'}),
            'anio_publicacion': forms.NumberInput(attrs={'class': 'form-control'}),
            'paginas': forms.NumberInput(attrs={'class': 'form-control'}),
            'stock_total': forms.NumberInput(attrs={'class': 'form-control'}),
            'disponibles': forms.NumberInput(attrs={'class': 'form-control'}),
            'sinopsis': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'anio_publicacion': 'Año de publicación',
            'stock_total': 'Stock total',
            'disponibles': 'Ejemplares disponibles',
        }
        help_texts = {
            'disponibles': 'No puede ser mayor al stock total.',
        }

    # ===== Nivel 1: validación por campo =====
    def clean_titulo(self):
        titulo = sanitize_input(self.cleaned_data.get('titulo'))
        if len(titulo) < 3:
            raise ValidationError('El título debe tener al menos 3 caracteres.')
        if len(titulo) > 200:
            raise ValidationError('El título no puede superar 200 caracteres.')
        return titulo

    def clean_isbn(self):
        # Nota: validar_isbn (checksum) ya corrió en el campo.
        # Aquí nos encargamos de normalizar y verificar unicidad.
        isbn = re.sub(r'[\s-]', '', self.cleaned_data.get('isbn', ''))
        qs = Libro.objects.filter(isbn=isbn)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('Ya existe un libro registrado con este ISBN.')
        return isbn

    def clean_sinopsis(self):
        return sanitize_input(self.cleaned_data.get('sinopsis', ''))

    # ===== Nivel 2: validación cross-field =====
    def clean(self):
        cleaned = super().clean()
        stock = cleaned.get('stock_total')
        disponibles = cleaned.get('disponibles')

        # add_error() permite acumular varios errores a la vez
        if stock is not None and disponibles is not None and disponibles > stock:
            self.add_error(
                'disponibles',
                f'Los disponibles ({disponibles}) no pueden superar el stock total ({stock}).',
            )

        return cleaned


# ---------------------------------------------------------------
# Form clásico: búsqueda (no persiste)
# ---------------------------------------------------------------
class BusquedaLibroForm(forms.Form):
    query = forms.CharField(
        required=False,
        max_length=100,
        label='Buscar por título o ISBN',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: Cien años, 9780307474728',
        }),
    )
    categoria = forms.ModelChoiceField(
        queryset=Categoria.objects.all(),
        required=False,
        empty_label='— Todas las categorías —',
        label='Categoría',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    autor = forms.ModelChoiceField(
        queryset=Autor.objects.all(),
        required=False,
        empty_label='— Todos los autores —',
        label='Autor',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    solo_disponibles = forms.BooleanField(
        required=False,
        label='Solo con ejemplares disponibles',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )

    def clean_query(self):
        q = sanitize_input(self.cleaned_data.get('query', ''))
        if q and len(q) < 2:
            raise ValidationError('El término debe tener al menos 2 caracteres.')
        return q