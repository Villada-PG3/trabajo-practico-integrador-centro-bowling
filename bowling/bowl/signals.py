from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from .models import Usuario
from .models import Cliente

@receiver(post_save, sender=Usuario)
def asignar_grupo_por_rol(sender, instance, created, **kwargs):
    grupo, _ = Group.objects.get_or_create(name=instance.rol.capitalize())
    # Si Usuario tiene un campo 'user' ligado a Django User
    usuario_django = instance.user if hasattr(instance, 'user') else instance
    usuario_django.groups.clear()
    usuario_django.groups.add(grupo)
    
@receiver(post_save, sender=Usuario)
def crear_cliente_para_usuario(sender, instance, created, **kwargs):
    if created:
        Cliente.objects.create(
            user=instance,
            nombre=instance.username,
            direccion="",
            telefono="",
            email=instance.email
        )