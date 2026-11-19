from datetime import timedelta
from functools import wraps
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .forms import AutorForm, CategoriaForm, LibroForm, RegistroForm
from .models import Autor, Categoria, Libro, Perfil, Prestamo

def personal_requerido(view):
    @login_required
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not (request.user.is_superuser or request.user.is_staff or getattr(getattr(request.user,'perfil',None),'rol',None) == Perfil.BIBLIOTECARIO):
            raise PermissionDenied
        return view(request,*args,**kwargs)
    return wrapped

def inicio(request):
    libros = Libro.objects.filter(activo=True).select_related('autor','categoria').order_by('-creado')[:6]
    return render(request,'core/inicio.html',{'libros':libros,'cantidad':Libro.objects.filter(activo=True).count()})

def catalogo(request):
    libros = Libro.objects.filter(activo=True).select_related('autor','categoria')
    q = request.GET.get('q','').strip()
    categoria = request.GET.get('categoria','')
    if q:
        libros = libros.filter(Q(titulo__icontains=q)|Q(autor__nombre__icontains=q)|Q(isbn__icontains=q))
    if categoria.isdigit():
        libros = libros.filter(categoria_id=int(categoria))
    return render(request,'core/catalogo.html',{'libros':libros,'categorias':Categoria.objects.all(),'q':q,'categoria_actual':categoria})

def detalle(request,pk):
    libro = get_object_or_404(Libro.objects.select_related('autor','categoria'),pk=pk,activo=True)
    solicitado = request.user.is_authenticated and Prestamo.objects.filter(usuario=request.user,libro=libro,estado__in=[Prestamo.SOLICITADO,Prestamo.PRESTADO]).exists()
    return render(request,'core/detalle.html',{'libro':libro,'solicitado':solicitado})

def registro(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = RegistroForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request,user)
        messages.success(request,'Tu cuenta se creó correctamente.')
        return redirect('dashboard')
    return render(request,'core/formulario.html',{'form':form,'titulo':'Crear cuenta','subtitulo':'Registra tu cuenta para solicitar préstamos.','boton':'Registrarme'})

@login_required
def dashboard(request):
    if request.user.is_superuser or request.user.is_staff or getattr(getattr(request.user,'perfil',None),'rol',None) == Perfil.BIBLIOTECARIO:
        return redirect('gestion')
    prestamos = Prestamo.objects.filter(usuario=request.user).select_related('libro')[:5]
    return render(request,'core/dashboard.html',{'prestamos':prestamos,'activos':Prestamo.objects.filter(usuario=request.user,estado=Prestamo.PRESTADO).count()})

@login_required
def mis_prestamos(request):
    return render(request,'core/mis_prestamos.html',{'prestamos':Prestamo.objects.filter(usuario=request.user).select_related('libro')})

@login_required
def solicitar(request,pk):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    libro = get_object_or_404(Libro,pk=pk,activo=True)
    with transaction.atomic():
        libro = Libro.objects.select_for_update().get(pk=libro.pk)
        if libro.disponibles <= 0:
            messages.error(request,'No hay ejemplares disponibles.')
        elif Prestamo.objects.filter(libro=libro,usuario=request.user,estado__in=[Prestamo.SOLICITADO,Prestamo.PRESTADO]).exists():
            messages.warning(request,'Ya tienes una solicitud o préstamo activo para este libro.')
        else:
            Prestamo.objects.create(libro=libro,usuario=request.user)
            messages.success(request,'Solicitud registrada. El bibliotecario debe aprobarla.')
    return redirect('detalle',pk=pk)

@personal_requerido
def gestion(request):
    return render(request,'core/gestion.html',{
        'total_libros':Libro.objects.count(),
        'pendientes':Prestamo.objects.filter(estado=Prestamo.SOLICITADO).count(),
        'en_prestamo':Prestamo.objects.filter(estado=Prestamo.PRESTADO).count(),
        'ultimos':Prestamo.objects.select_related('libro','usuario')[:7],
    })

@personal_requerido
def gestion_libros(request):
    libros = Libro.objects.select_related('autor','categoria').all()
    q = request.GET.get('q','').strip()
    if q:
        libros = libros.filter(Q(titulo__icontains=q)|Q(isbn__icontains=q))
    return render(request,'core/gestion_libros.html',{'libros':libros,'q':q})

@personal_requerido
def libro_crear(request):
    form = LibroForm(request.POST or None,request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request,'Libro registrado.')
        return redirect('gestion_libros')
    return render(request,'core/formulario.html',{'form':form,'titulo':'Registrar libro','boton':'Guardar libro','volver':'gestion_libros'})

@personal_requerido
def libro_editar(request,pk):
    libro = get_object_or_404(Libro,pk=pk)
    form = LibroForm(request.POST or None,request.FILES or None,instance=libro)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request,'Libro actualizado.')
        return redirect('gestion_libros')
    return render(request,'core/formulario.html',{'form':form,'titulo':'Editar libro','boton':'Guardar cambios','volver':'gestion_libros'})

@personal_requerido
def autor_crear(request):
    form = AutorForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request,'Autor registrado.')
        return redirect('libro_crear')
    return render(request,'core/formulario.html',{'form':form,'titulo':'Registrar autor','boton':'Guardar autor','volver':'libro_crear'})

@personal_requerido
def categoria_crear(request):
    form = CategoriaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request,'Categoría registrada.')
        return redirect('libro_crear')
    return render(request,'core/formulario.html',{'form':form,'titulo':'Registrar categoría','boton':'Guardar categoría','volver':'libro_crear'})

@personal_requerido
def gestion_prestamos(request):
    estado = request.GET.get('estado','')
    prestamos = Prestamo.objects.select_related('libro','usuario').all()
    if estado in dict(Prestamo.ESTADOS):
        prestamos = prestamos.filter(estado=estado)
    return render(request,'core/gestion_prestamos.html',{'prestamos':prestamos,'estados':Prestamo.ESTADOS,'estado_actual':estado})

@personal_requerido
def procesar_prestamo(request,pk,accion):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    with transaction.atomic():
        prestamo = get_object_or_404(Prestamo.objects.select_for_update(),pk=pk)
        libro = Libro.objects.select_for_update().get(pk=prestamo.libro_id)
        if accion == 'aprobar' and prestamo.estado == Prestamo.SOLICITADO:
            if libro.disponibles < 1:
                messages.error(request,'No hay ejemplares disponibles.')
            else:
                prestamo.estado = Prestamo.PRESTADO
                prestamo.fecha_prestamo = timezone.now()
                prestamo.fecha_limite = timezone.localdate() + timedelta(days=14)
                prestamo.gestionado_por = request.user
                prestamo.save(update_fields=['estado','fecha_prestamo','fecha_limite','gestionado_por'])
                messages.success(request,'Préstamo aprobado.')
        elif accion == 'rechazar' and prestamo.estado == Prestamo.SOLICITADO:
            prestamo.estado = Prestamo.RECHAZADO
            prestamo.gestionado_por = request.user
            prestamo.save(update_fields=['estado','gestionado_por'])
            messages.success(request,'Solicitud rechazada.')
        elif accion == 'devolver' and prestamo.estado == Prestamo.PRESTADO:
            prestamo.estado = Prestamo.DEVUELTO
            prestamo.fecha_devolucion = timezone.now()
            prestamo.gestionado_por = request.user
            prestamo.save(update_fields=['estado','fecha_devolucion','gestionado_por'])
            messages.success(request,'Devolución registrada.')
        else:
            messages.error(request,'Operación no permitida para el estado actual.')
    return redirect('gestion_prestamos')
