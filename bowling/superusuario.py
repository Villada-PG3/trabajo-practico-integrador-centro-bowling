import os
import django

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth.models import User

# Crear el superusuario si no existe
if not User.objects.filter(username="admin").exists():
    User.objects.create_superuser("admin", "", "1234")
    print("✅ Superusuario creado: admin / 1234")
else:
    print("ℹ️ Ya existe el superusuario 'admin'")
