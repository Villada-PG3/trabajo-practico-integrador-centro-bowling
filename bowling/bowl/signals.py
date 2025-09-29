from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Reserva, Pista, Estado

@receiver(post_save, sender=Reserva)
def marcar_pista_ocupada(sender, instance, created, **kwargs):
    if created:
        try:
            ocupado = Estado.objects.get(nombre='Ocupado')
            pista = instance.pista
            pista.estado = ocupado
            pista.save()
        except Estado.DoesNotExist:
            pass

@receiver(post_delete, sender=Reserva)
def liberar_pista(sender, instance, **kwargs):
    try:
        libre = Estado.objects.get(nombre='Libre')
        pista = instance.pista
        pista.estado = libre
        pista.save()
    except Estado.DoesNotExist:
        pass
