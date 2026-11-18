"""
Validadores personalizados del dominio BookHub.
Se ejecutan en la fase `to_python`/`validate` del campo de formulario,
ANTES de clean_<campo>() y clean().
"""
import re

from django.core.exceptions import ValidationError
from django.utils import timezone


def validar_isbn(value: str) -> None:
    """
    Valida ISBN-10 o ISBN-13.
    Acepta guiones y espacios, pero verifica:
      - Longitud correcta (10 o 13 dígitos)
      - Checksum ISBN-13 correcto (dígito verificador)
    """
    isbn = re.sub(r'[\s-]', '', value or '')
    if not re.fullmatch(r'\d{10}|\d{13}', isbn):
        raise ValidationError(
            'ISBN inválido: debe tener 10 o 13 dígitos (puedes usar guiones).',
            code='isbn_longitud',
        )

    if len(isbn) == 13:
        suma = sum(
            int(d) * (1 if i % 2 == 0 else 3)
            for i, d in enumerate(isbn[:12])
        )
        checksum = (10 - (suma % 10)) % 10
        if checksum != int(isbn[12]):
            raise ValidationError(
                'ISBN-13 inválido: el dígito verificador no coincide.',
                code='isbn_checksum',
            )


def validar_anio_publicacion(value: int) -> None:
    """El año debe estar entre 1000 y el año actual."""
    if value < 1000:
        raise ValidationError('El año de publicación debe ser mayor a 999.')
    if value > timezone.now().year:
        raise ValidationError(
            f'El año no puede ser posterior a {timezone.now().year}.'
        )


def validar_no_solo_espacios(value: str) -> None:
    """Rechaza cadenas vacías o compuestas solo de espacios."""
    if not value or not str(value).strip():
        raise ValidationError('Este campo no puede estar vacío ni contener solo espacios.')