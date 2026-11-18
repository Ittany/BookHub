from django.test import TestCase
from django.urls import reverse
from .forms import LibroForm, RegistroAvanzadoForm
from .models import Autor

class LibroFormTests(TestCase):

    def setUp(self):
        self.autor = Autor.objects.create(nombre='Gabriel', apellido='García Márquez')

    def _data(self, **overrides):
        data = {
            'titulo': 'Cien años de soledad',
            'autor': self.autor.pk,
            'isbn': '9780307474728',
            'anio_publicacion': 1967,
            'paginas': 471,
            'stock_total': 3,
            'disponibles': 2,
            'sinopsis': 'Novela de realismo mágico.',
            'activo': True,
        }
        data.update(overrides)
        return data

    def test_formulario_valido(self):
        form = LibroForm(data=self._data())
        self.assertTrue(form.is_valid(), form.errors)

    def test_isbn_checksum_invalido(self):
        form = LibroForm(data=self._data(isbn='9780307474729'))
        self.assertFalse(form.is_valid())
        self.assertIn('isbn', form.errors)

    def test_disponibles_mayor_que_stock(self):
        form = LibroForm(data=self._data(disponibles=10))
        self.assertFalse(form.is_valid())
        self.assertIn('disponibles', form.errors)

    def test_titulo_sanitizado(self):
        form = LibroForm(data=self._data(titulo='  <b>Rayuela</b>  '))
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['titulo'], 'Rayuela')

class RegistroAvanzadoFormTests(TestCase):
    def test_multi_error_asunto(self):
        form = RegistroAvanzadoForm(data={
            'nombre_contacto': 'Ana',
            'email_contacto': 'ana@x.com',
            'asunto': 'a<b',
            'mensaje': 'Hola',
            'acepta_politica': True,
        })
        self.assertFalse(form.is_valid())
        self.assertGreaterEqual(len(form.errors['asunto']), 2)

    def test_acepta_politica_en_non_field_errors(self):
        form = RegistroAvanzadoForm(data={
            'nombre_contacto': 'Ana',
            'email_contacto': 'ana@x.com',
            'asunto': 'Consulta general',
            'mensaje': 'Hola',
            'acepta_politica': False,
        })
        self.assertFalse(form.is_valid())
        self.assertTrue(form.non_field_errors())