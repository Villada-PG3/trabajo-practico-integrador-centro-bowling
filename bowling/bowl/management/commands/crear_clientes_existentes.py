from django.core.management.base import BaseCommand
from django.conf import settings
from bowl.models import Usuario, Cliente

class Command(BaseCommand):
    help = "Crea clientes para todos los usuarios que aún no tienen uno"

    def handle(self, *args, **kwargs):
        usuarios = Usuario.objects.all()
        creados = 0
        for user in usuarios:
            if not hasattr(user, "cliente"):
                Cliente.objects.create(
                    user=user,
                    nombre=user.username,
                    direccion="",
                    telefono="",
                    email=user.email
                )
                creados += 1
                self.stdout.write(self.style.SUCCESS(f"Cliente creado para {user.username}"))
        self.stdout.write(self.style.SUCCESS(f"Total de clientes creados: {creados}"))
