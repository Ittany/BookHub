from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import BusquedaLibroForm, LibroForm
from .models import Libro


def lista_libros(request):
    """GET → muestra catálogo + filtros. Nunca guarda."""
    form = BusquedaLibroForm(request.GET or None)
    libros = (
        Libro.objects
        .select_related('autor')          # evita N+1
        .prefetch_related('categoria')    # evita N+1 en M2M
        .filter(activo=True)
    )

    if form.is_valid():
        q = form.cleaned_data.get('query')
        categoria = form.cleaned_data.get('categoria')
        autor = form.cleaned_data.get('autor')
        solo_disponibles = form.cleaned_data.get('solo_disponibles')

        if q:
            libros = libros.filter(
                Q(titulo__icontains=q) | Q(isbn__icontains=q)
            )
        if categoria:
            libros = libros.filter(categoria=categoria)
        if autor:
            libros = libros.filter(autor=autor)
        if solo_disponibles:
            libros = libros.filter(disponibles__gt=0)

    return render(request, 'catalogo/lista_libros.html', {
        'libros': libros,
        'form': form,
        'total': libros.count(),
    })


def crear_libro(request):
    """
    Ciclo completo del formulario:
      GET  → instancia vacía → render
      POST → bind → is_valid()
               ├─ OK  → save() → redirect
               └─ MAL → form con errors → render
    """
    if request.method == 'POST':
        form = LibroForm(request.POST)          # 🔑 bind al POST
        if form.is_valid():
            libro = form.save()
            messages.success(request, f'Libro «{libro.titulo}» registrado.')
            return redirect('catalogo:detalle_libro', pk=libro.pk)
        else:
            messages.error(request, 'Revisa los errores del formulario.')
    else:
        form = LibroForm()                       # instancia vacía

    return render(request, 'catalogo/crear_libro.html', {'form': form})


def detalle_libro(request, pk):
    libro = get_object_or_404(
        Libro.objects.select_related('autor').prefetch_related('categoria'),
        pk=pk,
    )
    return render(request, 'catalogo/detalle_libro.html', {'libro': libro})