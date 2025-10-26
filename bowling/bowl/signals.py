from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from .models import Usuario, Cliente


@receiver(post_save, sender=Usuario)
def asignar_grupo_por_rol(sender, instance, created, **kwargs):
    # Crea o obtiene un grupo con el mismo nombre que el rol del usuario
    grupo, _ = Group.objects.get_or_create(name=instance.rol.capitalize())

    # Usa 'user' si el modelo Usuario está vinculado al modelo User de Django
    usuario_django = instance.user if hasattr(instance, 'user') else instance

    # Limpia grupos anteriores y asigna el correspondiente
    usuario_django.groups.clear()
    usuario_django.groups.add(grupo)


@receiver(post_save, sender=Usuario)
def crear_cliente_para_usuario(sender, instance, created, **kwargs):
    # Solo al crear un nuevo usuario, genera automáticamente su cliente asociado
    if created:
        Cliente.objects.create(
            user=instance,
            nombre=instance.username,
            direccion="",
            telefono="",
            email=instance.email
        )
