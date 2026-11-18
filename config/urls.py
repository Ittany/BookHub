from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cuentas/login/', auth_views.LoginView.as_view(), name='login'),
    path('cuentas/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('cuentas/', include('cuentas.urls')),
    path('catalogo/', include('catalogo.urls')),
    path('', include('catalogo.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)