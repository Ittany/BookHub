import logging
import time
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('bookhub.audit')


class AuditoriaMiddleware(MiddlewareMixin):
    """
    Intercepta request/response. Mide duración y registra accesos a rutas
    sensibles (/admin/, /catalogo/nuevo/).
    Orden LIFO: se ejecuta en el orden de MIDDLEWARE en settings.py.
    """

    RUTAS_SENSIBLES = ('/admin/', '/catalogo/nuevo/')

    def __call__(self, request):
        inicio = time.perf_counter()
        response = super().__call__(request)     # ejecuta la vista
        duracion_ms = (time.perf_counter() - inicio) * 1000

        if any(request.path.startswith(r) for r in self.RUTAS_SENSIBLES):
            user = getattr(request, 'user', None)
            username = user.get_username() if user and user.is_authenticated else 'anónimo'
            logger.warning(
                'AUDIT %s %s user=%s status=%s duracion=%.1fms',
                request.method, request.path, username,
                response.status_code, duracion_ms,
            )
            # Header de diagnóstico (no en producción)
            response['X-BookHub-Audit'] = f'{duracion_ms:.0f}ms'
        return response