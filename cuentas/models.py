from django.apps import AppConfig

class CuentasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cuentas'

    def ready(self):
        # Importar para registrar signal handlers
        from . import signals  # noqa: F401