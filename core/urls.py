from django.urls import path
from . import views
urlpatterns = [
 path('',views.inicio,name='inicio'),
 path('catalogo/',views.catalogo,name='catalogo'),
 path('catalogo/<int:pk>/',views.detalle,name='detalle'),
 path('registro/',views.registro,name='registro'),
 path('panel/',views.dashboard,name='dashboard'),
 path('mis-prestamos/',views.mis_prestamos,name='mis_prestamos'),
 path('catalogo/<int:pk>/solicitar/',views.solicitar,name='solicitar'),
 path('gestion/',views.gestion,name='gestion'),
 path('gestion/libros/',views.gestion_libros,name='gestion_libros'),
 path('gestion/libros/nuevo/',views.libro_crear,name='libro_crear'),
 path('gestion/libros/<int:pk>/editar/',views.libro_editar,name='libro_editar'),
 path('gestion/autores/nuevo/',views.autor_crear,name='autor_crear'),
 path('gestion/categorias/nueva/',views.categoria_crear,name='categoria_crear'),
 path('gestion/prestamos/',views.gestion_prestamos,name='gestion_prestamos'),
 path('gestion/prestamos/<int:pk>/<str:accion>/',views.procesar_prestamo,name='procesar_prestamo'),
]
