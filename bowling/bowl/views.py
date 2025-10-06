# bowl/views.py
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import TemplateView, ListView, CreateView, UpdateView
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.mail import send_mail
from .models import Reserva, Pista, Cafeteria, Mensaje
from .forms import PistaForm, CafeteriaForm, ContactoForm



# -------------------------
# Mixins
# -------------------------
class ThemeMixin:
    """Agrega theme_mode al contexto de todas las vistas que lo usen"""
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['theme_mode'] = self.request.session.get('theme_mode', 'light')
        return context

# -------------------------
# Vistas de Inicio y Tema
# -------------------------
class InicioView(ThemeMixin, TemplateView):
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

# -------------------------
# Vistas de Reservas
# -------------------------
class ReservaView(LoginRequiredMixin, ThemeMixin, ListView):
    model = Reserva
    template_name = "bowl/reserva.html"
    context_object_name = "reservas"

    def get_queryset(self):
        return Reserva.objects.filter(usuario=self.request.user).order_by('-fecha', 'hora')

# -------------------------
# Vistas de Pistas
# -------------------------
class ListaPistasView(LoginRequiredMixin, ThemeMixin, ListView):
    model = Pista
    template_name = "bowl/cositas_admin/lista_pistas.html"
    context_object_name = "pistas"

class CrearPistaView(LoginRequiredMixin, ThemeMixin, CreateView):
    model = Pista
    form_class = PistaForm
    template_name = "bowl/cositas_admin/crear_pistas.html"
    success_url = reverse_lazy('lista_pistas')

class EditarPistaView(LoginRequiredMixin, ThemeMixin, UpdateView):
    model = Pista
    form_class = PistaForm
    template_name = "bowl/cositas_admin/editar_pistas.html"
    success_url = reverse_lazy('lista_pistas')

# -------------------------
# Vistas de Cafetería
# -------------------------
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

# -------------------------
# VISTA DE CONTACTO
# -------------------------

class ContactoView(View):
    template_name = "bowl/contactos.html"

    def get(self, request):
        form = ContactoForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = ContactoForm(request.POST)
        if form.is_valid():
            # Guardar o enviar el mensaje, según tu lógica
            form.save()
            messages.success(request, "¡Mensaje enviado con éxito!")
            return redirect('contacto')
        return render(request, self.template_name, {'form': form})
    
