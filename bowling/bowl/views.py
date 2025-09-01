from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

def inicio(request):
    return render(request, 'bowl/inicio.html')
def reserva(request):
    return render(request, 'bowl/reserva.html')

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