from django.contrib import admin
from django.db.models import Count, F, Q
from django.utils.html import format_html
from .models import Autor, Categoria, Libro

admin.site.site_header = "BookHub — Administración"
admin.site.site_title = "BookHub Admin"
admin.site.index_title = "Panel operativo"


class LibroInline(admin.TabularInline):
    model = Libro
    extra = 0
    fields = ('titulo', 'isbn', 'anio_publicacion', 'disponibles', 'stock_total')
    readonly_fields = ('isbn',)
    show_change_link = True


@admin.register(Autor)
class AutorAdmin(admin.ModelAdmin):
    list_display = ('nombre_completo', 'nacionalidad', 'total_libros')
    list_filter = ('nacionalidad',)
    search_fields = ('nombre', 'apellido')
    ordering = ('apellido', 'nombre')
    inlines = [LibroInline]

    def get_queryset(self, request):
        # select_related + annotate para evitar N+1
        qs = super().get_queryset(request)
        return qs.annotate(_total_libros=Count('libros'))

    @admin.display(description='Libros', ordering='_total_libros')
    def total_libros(self, obj):
        return obj._total_libros


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug', 'total_libros')
    prepopulated_fields = {'slug': ('nombre',)}
    search_fields = ('nombre',)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_total_libros=Count('libros'))

    @admin.display(description='Libros', ordering='_total_libros')
    def total_libros(self, obj):
        return obj._total_libros


@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = (
        'titulo', 'autor', 'anio_publicacion',
        'estado_stock', 'disponibles', 'stock_total', 'activo',
    )
    list_filter = ('activo', 'categoria', 'anio_publicacion')
    search_fields = ('titulo', 'isbn', 'autor__nombre', 'autor__apellido')
    readonly_fields = ('fecha_alta', 'fecha_actualizacion', 'estado_stock')
    list_select_related = ('autor',)          # select_related en el admin
    filter_horizontal = ('categoria',)         # M2M más cómodo
    list_per_page = 25
    date_hierarchy = 'fecha_alta'
    actions = ['marcar_inactivos', 'reponer_disponibles']

    fieldsets = (
        ('Información básica', {
            'fields': ('titulo', 'autor', 'categoria', 'isbn', 'anio_publicacion', 'paginas')
        }),
        ('Inventario', {
            'fields': ('stock_total', 'disponibles', 'estado_stock')
        }),
        ('Contenido', {
            'fields': ('sinopsis',),
            'classes': ('collapse',),
        }),
        ('Estado y auditoría', {
            'fields': ('activo', 'fecha_alta', 'fecha_actualizacion'),
            'classes': ('collapse',),
        }),
    )

    # ---- Campo calculado con @admin.display ----
    @admin.display(description='Estado stock')
    def estado_stock(self, obj):
        if not obj.pk:
            return '—'
        if obj.disponibles == 0:
            return format_html('<span style="color:#b91c1c;">🔴 Agotado</span>')
        if obj.disponibles < obj.stock_total:
            return format_html('<span style="color:#d97706;">🟡 Parcial</span>')
        return format_html('<span style="color:#047857;">🟢 Disponible</span>')

    # ---- Acciones masivas ----
    @admin.action(description='Marcar libros seleccionados como inactivos')
    def marcar_inactivos(self, request, queryset):
        n = queryset.update(activo=False)
        self.message_user(request, f'{n} libro(s) marcados como inactivos.')

    @admin.action(description='Reponer disponibles al stock total')
    def reponer_disponibles(self, request, queryset):
        n = queryset.update(disponibles=F('stock_total'))
        self.message_user(request, f'{n} libro(s) repuestos al stock total.')