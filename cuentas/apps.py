from django.apps import AppConfig


class CuentasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cuentas'
    verbose_name = 'Cuentas'

    def ready(self):
        # Importa los signals para registrar los receptores post_migrate.
        from . import signals  # noqa: F401