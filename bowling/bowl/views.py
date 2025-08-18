from django.shortcuts import render
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Reserva

def inicio(request):
    return render(request, 'bowl/inicio.html')
def reserva(request):
    return render(request, 'bowl/reserva.html')




#class ReservaView(LoginRequiredMixin, ListView):
class ReservaView(ListView):
    model = Reserva
    template_name = 'bowl/reserva.html'  # tu template
    context_object_name = 'reservas'

    def get_queryset(self):
        # Filtra solo las reservas del cliente logueado
        return Reserva.objects.all
        #return Reserva.objects.filter(cliente__user=self.request.user)