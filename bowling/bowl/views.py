from django.shortcuts import render
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Reserva

def inicio(request):
    return render(request, 'bowl/inicio.html')

def reserva(request):
    return render(request, 'bowl/reserva.html')

def cafe(request):
    return render(request, 'bowl/cafe.html')

class ReservaView(ListView):
    model = Reserva
    template_name = "bowl/reservas.html"
    context_object_name="reservas"