from django.contrib import admin
from .models import Autor, Categoria, Libro

admin.site.site_header = "BookHub — Administración"
admin.site.site_title = "BookHub Admin"


@admin.register(Autor)
class AutorAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'nacionalidad')
    search_fields = ('nombre', 'apellido')


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug')
    prepopulated_fields = {'slug': ('nombre',)}
    search_fields = ('nombre',)


@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'anio_publicacion', 'disponibles', 'stock_total', 'activo')
    list_filter = ('activo', 'categoria')
    search_fields = ('titulo', 'isbn', 'autor__nombre', 'autor__apellido')