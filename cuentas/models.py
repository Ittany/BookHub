from django.db import models  # noqa: F401

# BookHub usa el modelo User nativo de django.contrib.auth.
# Este archivo queda vacío intencionalmente; los roles se implementan
# con Groups + Permissions en cuentas/signals.py.