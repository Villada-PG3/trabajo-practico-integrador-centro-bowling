from django.shortcuts import render
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Reserva

# bowl/views.py
from django.shortcuts import render, redirect

def inicio(request):
    """
    Renders the dashboard page, passing the user's theme preference.
    """
    # Get the theme mode from the session, defaulting to 'light'
    theme_mode = request.session.get('theme_mode', 'light')
    
    context = {
        'theme_mode': theme_mode,
    }
    return render(request, 'bowl/inicio.html', context)

def toggle_theme_mode(request):
    """
    Toggles the theme mode between 'light' and 'dark' in the user's session.
    """
    current_mode = request.session.get('theme_mode', 'light')
    if current_mode == 'light':
        request.session['theme_mode'] = 'dark'
    else:
        request.session['theme_mode'] = 'light'
        
    # Redirect the user back to the page they came from
    return redirect(request.META.get('HTTP_REFERER', 'inicio'))
def reserva(request):
    return render(request, 'bowl/reserva.html')

<<<<<<< HEAD
def cafe(request):
    return render(request, 'bowl/cafeteria.html')
class ReservaView(ListView):
    model = Reserva
    template_name = "bowl/reservas.html"
    context_object_name="reservas"
=======
class ReservaView(LoginRequiredMixin, ListView):
    model = Reserva
    template_name = "bowl/reserva.html"
    context_object_name = "reservas"

    def get_queryset(self):
        return Reserva.objects.filter(usuario=self.request.user).order_by('-fecha', 'hora')
>>>>>>> 6495302980e21e611f57760f2516a3dabdef3b1a
