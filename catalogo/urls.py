from django.urls import path
from . import views

app_name = 'catalogo'

urlpatterns = [
    path('', views.lista_libros, name='lista_libros'),
    path('nuevo/', views.crear_libro, name='crear_libro'),
    path('<int:pk>/', views.detalle_libro, name='detalle_libro'),
    path('contacto/', views.contacto_avanzado, name='contacto_avanzado'),
]