# bowl/views.py
from django.shortcuts import redirect, render
from django.views.generic import TemplateView, ListView, CreateView, UpdateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Reserva, Pista, Cafeteria
from .forms import PistaForm, CafeteriaForm, CrearPistaForm, EditarPistaForm

class ThemeMixin:
    """Agrega theme_mode al contexto de todas las vistas que lo usen"""
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['theme_mode'] = self.request.session.get('theme_mode', 'light')



# ---------- Vistas de Inicio y Tema ----------
class InicioView(TemplateView, ThemeMixin):
    template_name = "bowl/inicio.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['estado_logueo'] = 0
        return context


def toggle_theme_mode(request):
    """Alterna entre light y dark"""
    current_mode = request.session.get('theme_mode', 'light')
    request.session['theme_mode'] = 'dark' if current_mode == 'light' else 'light'
    return redirect(request.META.get('HTTP_REFERER', 'inicio'))


class CafeView(LoginRequiredMixin, ThemeMixin, TemplateView):
    template_name = "bowl/cafe.html"


class LoginnView(ThemeMixin, LoginView):
    template_name = "bowl/inicio_sesion1.html"


# ---------- Vistas de Reservas ----------
class ReservaView(LoginRequiredMixin, ThemeMixin, ListView):
    model = Reserva
    template_name = "bowl/reserva.html"
    context_object_name = "reservas"

    def get_queryset(self):
        return Reserva.objects.filter(usuario=self.request.user).order_by('-fecha', 'hora')


# ---------- Vistas de Pistas ----------
class ListaPistasView(LoginRequiredMixin, ListView):
    model = Pista
    template_name = "bowl/cositas_admin/lista_pistas.html"
    context_object_name = "pistas"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Esto asegura que pasamos todas las pistas
        context['pistas'] = Pista.objects.all()
        return context


class CrearPistaView(CreateView):
    model = Pista
    form_class = CrearPistaForm
    template_name = "bowl/cositas_admin/crear_pistas.html"
    success_url = reverse_lazy('lista_pistas')  # adonde redirige después de crear


class EditarPistaView(LoginRequiredMixin, ThemeMixin, UpdateView):
    model = Pista
    form_class = EditarPistaForm
    template_name = "bowl/cositas_admin/editar_pistas.html"
    success_url = reverse_lazy('lista_pistas')


# ---------- Vistas de Cafeteria ----------
class ListaComidaView(LoginRequiredMixin, ThemeMixin, ListView):
    model = Cafeteria
    template_name = "bowl/cositas_admin/lista_comidas.html"
    context_object_name = "cafeteria"


class CrearCafeteriaView(LoginRequiredMixin, ThemeMixin, CreateView):
    model = Cafeteria
    form_class = CafeteriaForm
    template_name = "bowl/cositas_admin/crear_comida.html"
    success_url = reverse_lazy('lista_comida')


class EditarCafeteriaView(LoginRequiredMixin, ThemeMixin, UpdateView):
    model = Cafeteria
    form_class = CafeteriaForm
    template_name = "bowl/cositas_admin/editar_comida.html"
    success_url = reverse_lazy('lista_comida')


