from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

def inicio(request):
    return render(request, 'bowl/inicio.html')
def reserva(request):
    return render(request, 'bowl/reserva.html')
def hola(request):
    return render(request, "bowl/inicio1.html")
def holaa(request):
    return render(request, "bowl/inicio_sesion1.html")
