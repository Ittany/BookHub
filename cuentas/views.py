from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import render
from django.views.generic import ListView

from catalogo.models import Libro


@login_required
def mi_cuenta(request):
    return render(request, 'cuentas/mi_cuenta.html')


class PanelBibliotecarioView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Libro
    template_name = 'cuentas/panel_bibliotecario.html'
    context_object_name = 'libros'
    permission_required = 'catalogo.change_libro'
    raise_exception = False  # Si autenticado sin permiso: redirige a LOGIN_URL

    def get_queryset(self):
        return Libro.objects.select_related('autor').all()


@permission_required('catalogo.add_libro', raise_exception=True)
def zona_creacion(request):
    """Ejemplo de FBV con permission_required. Si no tiene permiso: 403."""
    return render(request, 'cuentas/zona_creacion.html')