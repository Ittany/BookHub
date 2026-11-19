# BookHub — Sistema backend Django 5.x

Práctica de gestión de datos y seguridad en Django 5.x. El proyecto implementa un sistema de roles (Administrador, Bibliotecario y Lector) para la gestión de una biblioteca, incluyendo autores, libros, préstamos e historial.

## Stack

- Python 3.14
- Django 5.2.19
- SQLite
- django-extensions, python-decouple

## Requisitos previos

- Python 3.11+ (probado en 3.14)
- Git
- PowerShell o terminal equivalente

## Instalación

```bash
git clone https://github.com/Ittany/BookHub.git
cd BookHub

python -m venv venv

# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

BookHub_/
├── .venv/               # Entorno virtual
├── capturas/            # Capturas de pantalla del sistema
├── config/              # Configuración principal de Django
├── core/                # Aplicación principal (lógica de negocio)
├── media/               # Archivos subidos (ej. portadas)
├── static/              # Archivos estáticos (CSS, JS, imágenes)
├── templates/           # Plantillas HTML
│   ├── core/
│   └── registration/    # Plantillas de autenticación (login.html)
├── .env.example         # Ejemplo de variables de entorno
├── .gitignore
├── db.sqlite3           # Base de datos SQLite
├── manage.py
├── README.md
└── requirements.txt

Capturas de Pantalla
A continuación se muestra el flujo y las interfaces del sistema (ubicadas en la carpeta capturas/).

| Iniciar Sesión | Panel de Administrador |
| :---: | :---: |
| ![Iniciar Sesión](capturas/captura07.png) | ![Iniciar Sesión](capturas/captura02.png) | 
| Iniciar Sesión | Panel de Bibliotecario |

| ![Panel Admin](capturas/captura01.png) |![Panel Admin](capturas/captura03.png) |

| Panel de Bibliotecario | Panel de Lector |
| :---: | :---: |
| ![Panel Bibliotecario](capturas/captura08.png) | ![Panel Lector](capturas/captura11.png) |

### Gestión de Catálogo

| Agregar Libro | Agregar Autor || Catálogo agregados |
| :---: | :---: |
| ![Agregar Libro](capturas/captura05.png) | ![Agregar Autor](capturas/captura04.png) |![Agregar Autor](capturas/captura06.png) |

### Préstamos y Historial

| Préstamo de Libro | Historial de Libros Prestados |
| :---: | :---: |
| ![Préstamo de Libro](capturas/captura09.png) | ![Historial de Préstamos](capturas/captura10.png) |