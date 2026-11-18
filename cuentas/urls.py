from django.urls import path

from . import views

app_name = 'cuentas'

urlpatterns = [
    path('mi-cuenta/', views.mi_cuenta, name='mi_cuenta'),
    path('panel/', views.PanelBibliotecarioView.as_view(), name='panel_bibliotecario'),
    path('zona-creacion/', views.zona_creacion, name='zona_creacion'),
]