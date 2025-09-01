from django.shortcuts import render
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Reserva

def inicio(request):
    return render(request, 'bowl/inicio.html')

def reserva(request):
    return render(request, 'bowl/reserva.html')

class ReservaView(LoginRequiredMixin, ListView):
    model = Reserva
    template_name = "bowl/reserva.html"
    context_object_name = "reservas"

    def get_queryset(self):
        return Reserva.objects.filter(usuario=self.request.user).order_by('-fecha', 'hora')
