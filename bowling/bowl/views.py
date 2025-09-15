# bowl/views.py
from django.shortcuts import redirect
from django.views.generic import TemplateView, ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from .models import Reserva, Pista
from .forms import PistaForm


# ---------- Vistas de Inicio y Tema ----------
class InicioView(TemplateView):
    template_name = "bowl/inicio.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['theme_mode'] = self.request.session.get('theme_mode', 'light')
        return context


def toggle_theme_mode(request):
    """Función simple, no necesita CBV."""
    current_mode = request.session.get('theme_mode', 'light')
    request.session['theme_mode'] = 'dark' if current_mode == 'light' else 'light'
    return redirect(request.META.get('HTTP_REFERER', 'inicio'))


class CafeView(TemplateView):
    template_name = "bowl/cafe.html"


class IniciarSesionView(TemplateView):
    template_name = "bowl/inicio_sesion1.html"


# ---------- Vistas de Reservas ----------
class ReservaView(LoginRequiredMixin, ListView):
    model = Reserva
    template_name = "bowl/reserva.html"
    context_object_name = "reservas"

    def get_queryset(self):
        return Reserva.objects.filter(usuario=self.request.user).order_by('-fecha', 'hora')


# ---------- Vistas de Pistas ----------
class ListaPistasView(ListView):
    model = Pista
    template_name = "bowl/admin/lista_pistas.html"
    context_object_name = "pistas"


class CrearPistaView(CreateView):
    model = Pista
    form_class = PistaForm
    template_name = "bowl/admin/crear_pista.html"
    success_url = reverse_lazy('lista_pistas')


class EditarPistaView(UpdateView):
    model = Pista
    form_class = PistaForm
    template_name = "bowl/admin/editar_pista.html"
    success_url = reverse_lazy('lista_pistas')