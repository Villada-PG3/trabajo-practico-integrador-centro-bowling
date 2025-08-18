from django.shortcuts import render
from django.views.generic import ListView
from .models import Reserva

# Create your views here.
from django.shortcuts import render

def inicio(request):
    return render(request, 'bowl/inicio.html')
def reserva(request):
    return render(request, 'bowl/reserva.html')


class ReservaView(ListView):
    model = Reserva
    template_name = "bowl/reservas.html"  # tu HTML
    context_object_name = "reservas"  # nombre que usás en el template
