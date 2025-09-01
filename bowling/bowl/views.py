from django.shortcuts import render
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Reserva

def inicio(request):
    return render(request, 'bowl/inicio.html')

def reserva(request):
    return render(request, 'bowl/reserva.html')

class ReservaView(ListView):
    model = Reserva
    template_name = "bowl/reservas.html"
    context_object_name = "reservas"


def home(request):
    return render(request, 'bowl/home.html')

def pistas(request):
    return render(request, 'bowl/pistas.html')

def eventos(request):
    return render(request, 'bowl/eventos.html')

def cafeteria(request):  
    return render(request, 'bowl/cafeteria.html')

def contacto(request):
    return render(request, 'bowl/contacto.html')