"""
Middleware de BookHub.

Contiene:
  - AuditoriaMiddleware  → mide duración, loguea rutas sensibles, añade header.
  - CSPMiddleware        → añade Content-Security-Policy sin dependencias externas.

Orden LIFO: en settings.MIDDLEWARE el primero de la lista es el ÚLTIMO
en responder (se ejecuta "por fuera"). Respeta eso al registrarlos.
"""

import logging
import time

from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('bookhub.audit')


class AuditoriaMiddleware(MiddlewareMixin):
    """
    Intercepta request/response. Mide duración y registra accesos
    a rutas sensibles. Añade header X-BookHub-Audit solo en esas rutas.
    """

    RUTAS_SENSIBLES = ('/admin/', '/catalogo/nuevo/')

    def __call__(self, request):
        inicio = time.perf_counter()
        response = super().__call__(request)      # ejecuta la vista
        duracion_ms = (time.perf_counter() - inicio) * 1000

        if any(request.path.startswith(r) for r in self.RUTAS_SENSIBLES):
            user = getattr(request, 'user', None)
            username = user.get_username() if user and user.is_authenticated else 'anónimo'
            logger.warning(
                'AUDIT %s %s user=%s status=%s duracion=%.1fms',
                request.method,
                request.path,
                username,
                response.status_code,
                duracion_ms,
            )
            # Solo para diagnóstico en desarrollo (no expone datos sensibles)
            response['X-BookHub-Audit'] = f'{duracion_ms:.0f}ms'

        return response


class CSPMiddleware(MiddlewareMixin):
    """
    Content-Security-Policy mínima, sin django-csp.
    Debe ir lo MÁS AL EXTERIOR posible (primero en MIDDLEWARE)
    para aplicar la cabecera a TODAS las respuestas, incluidos errores.
    """

    def process_response(self, request, response):
        response['Content-Security-Policy'] = (
            "default-src 'self'; "
            "img-src 'self' data:; "
            "style-src 'self' 'unsafe-inline'; "
            "script-src 'self'; "
            "frame-ancestors 'none';"
        )
        return response