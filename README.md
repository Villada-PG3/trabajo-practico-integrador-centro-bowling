🎳 SpaceBowling

SpaceBowling es un sistema para un centro de bowling con cafetería. Permite administrar clientes, gestionar pistas por categoría (BASE, VIP, ULTRA VIP),
registrar reservas, partidas, jugadores y turnos, y controlar pedidos en la cafetería. También incluye sistema de contactos y gestión interna.

📂 Estructura relevante del Proyecto
----------------------------------------------------------------
| Carpeta / Archivo| Descripción                               | 
|------------------|-------------------------------------------|
| `bowling/`       | Carpeta raíz del proyecto                 |
| `bowl/`          | App principal del sistema                 |
| `bowl/static/`   | Archivos estáticos (CSS, PNG)             |
| `bowl/templates/`| Plantillas HTML                           |
| `bowl/admin.py`  | Registro de modelos en el panel admin     |
| `bowl/apps.py`   | Configuración de la app                   |
| `bowl/forms.py`  | Formularios Django                        |
| `bowl/models.py` | Modelos de la base de datos               |
| `bowl/views.py`  | Vistas del proyecto                       |
| `config/`        | Configuración general del proyecto Django |
| `docs/`          | Documentación y diagramas (Mermaid, PNG)  |
| `venv/`          | Entorno virtual (no subir a Git)          |
----------------------------------------------------------------

🛠 Requisitos

- Python 3.x
- Django 4.x
- SQLite3
- Librerías listadas en `requirements.txt` (attrs, bcrypt, Django, requests, pytz, rich, etc.)

⚡ Instalación y Ejecución

1. Clonar el repositorio y crear entorno virtual:
git clone https://github.com/Villada-PG3/trabajo-practico-integrador-centro-bowling.git
cd trabajo-practico-integrador-centro-bowling
python -m venv venv
.\venv\Scripts\activate   (en caso de usar windows=
pip install -r requirements.txt

Ejecutar migraciones:
python manage.py makemigrations
python manage.py migrate

Correr el servidor local:
python manage.py runserver

👤 Superusuario
Ya creado en la inicialización del proyecto. El usuario es admin_local, la contraseña es admin123
Acceder al panel de administración: http://127.0.0.1:8000/admin

📜 Licencia:
Proyecto de uso escolar.

🧑‍💻 Autores
Nicolás Ferreyra
Santiago Riccioni
Adriano Mancuso
Faustino Pedone
