from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from .models import Autor,Categoria,Libro,Perfil,Prestamo

class FlujoBibliotecaTests(TestCase):
    def setUp(self):
        self.autor=Autor.objects.create(nombre='Autora de prueba')
        self.categoria=Categoria.objects.create(nombre='Ciencia')
        self.libro=Libro.objects.create(titulo='Libro de prueba',autor=self.autor,categoria=self.categoria,isbn='9780000000001',ejemplares=1)
        self.lector=User.objects.create_user('lector',password='clave-segura-123')
        self.biblio=User.objects.create_user('bibliotecario',password='clave-segura-123')
        self.biblio.perfil.rol=Perfil.BIBLIOTECARIO
        self.biblio.perfil.save()
    def test_catalogo_publico(self):
        self.assertContains(self.client.get(reverse('catalogo')),'Libro de prueba')
    def test_lector_no_ve_gestion(self):
        self.client.force_login(self.lector)
        self.assertEqual(self.client.get(reverse('gestion')).status_code,403)
    def test_solicitud_aprobacion_y_devolucion(self):
        self.client.force_login(self.lector)
        self.assertEqual(self.client.post(reverse('solicitar',args=[self.libro.pk])).status_code,302)
        p=Prestamo.objects.get(usuario=self.lector)
        self.assertEqual(p.estado,Prestamo.SOLICITADO)
        self.client.force_login(self.biblio)
        self.client.post(reverse('procesar_prestamo',args=[p.pk,'aprobar']))
        p.refresh_from_db()
        self.assertEqual(p.estado,Prestamo.PRESTADO)
        self.assertEqual(self.libro.disponibles,0)
        self.client.post(reverse('procesar_prestamo',args=[p.pk,'devolver']))
        p.refresh_from_db()
        self.assertEqual(p.estado,Prestamo.DEVUELTO)
        self.assertEqual(self.libro.disponibles,1)
