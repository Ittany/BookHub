from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from catalogo.models import Libro


@receiver(post_migrate)
def crear_grupos_roles(sender, **kwargs):
    """Crea (idempotente) los roles bibliotecario y lector tras cada migrate."""
    if sender.name != 'cuentas':
        return

    ct_libro = ContentType.objects.get_for_model(Libro)

    # Bibliotecario: CRUD completo sobre Libro
    biblio, _ = Group.objects.get_or_create(name='bibliotecario')
    perms_biblio = Permission.objects.filter(
        content_type=ct_libro,
        codename__in=['add_libro', 'change_libro', 'delete_libro', 'view_libro'],
    )
    biblio.permissions.set(perms_biblio)

    # Lector: solo puede ver libros
    lector, _ = Group.objects.get_or_create(name='lector')
    perm_view = Permission.objects.filter(content_type=ct_libro, codename='view_libro')
    lector.permissions.set(perm_view)