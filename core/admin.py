from django.contrib import admin
from .models import Autor, Categoria, Libro, Perfil, Prestamo

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'rol', 'codigo']
    list_filter = ['rol']
    search_fields = ['usuario__username','usuario__email']

@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = ['titulo','autor','categoria','isbn','ejemplares','activo']
    list_filter = ['activo','categoria']
    search_fields = ['titulo','autor__nombre','isbn']

@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    list_display = ['libro','usuario','estado','solicitado','fecha_limite']
    list_filter = ['estado']
    search_fields = ['libro__titulo','usuario__username']
    readonly_fields = ['solicitado','fecha_prestamo','fecha_devolucion']

admin.site.register(Autor)
admin.site.register(Categoria)
