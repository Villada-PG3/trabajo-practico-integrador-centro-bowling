from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

def inicio(request):
    return render(request, 'bowl/inicio.html')
def reserva(request):
    return render(request, 'bowl/reserva.html')
