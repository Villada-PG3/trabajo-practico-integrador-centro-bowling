from django.core.management.base import BaseCommand
from django.conf import settings
from bowl.models import Usuario, Cliente

class Command(BaseCommand):
    
    help = "Crea clientes para todos los usuarios que aún no tienen uno"

    def handle(self, *args, **kwargs):
        # Obtener todos los usuarios del sistema
        usuarios = Usuario.objects.all()
        creados = 0  

        for user in usuarios:
            # Verificar si el usuario ya tiene un cliente asociado
            if not hasattr(user, "cliente"):
                # Crear un cliente asociado al usuario
                Cliente.objects.create(
                    user=user,
                    nombre=user.username,  # Nombre por defecto igual al username
                    direccion="",          
                    telefono="",           
                    email=user.email       
                )
                creados += 1
                # Mensaje de consola indicando creación exitosa
                self.stdout.write(self.style.SUCCESS(f"Cliente creado para {user.username}"))

        # Mensaje final mostrando la cantidad total de clientes creados
        self.stdout.write(self.style.SUCCESS(f"Total de clientes creados: {creados}"))
