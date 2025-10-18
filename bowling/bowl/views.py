# bowl/views.py
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import TemplateView, ListView, CreateView, UpdateView
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages

from .models import Reserva, Pista, Cafeteria
from .forms import PistaForm, CafeteriaForm, CrearPistaForm, EditarPistaForm

from django.core.mail import send_mail
from .models import Reserva, Pista, Cafeteria, Mensaje, Cliente
from .forms import PistaForm, CafeteriaForm, CrearPistaForm, EditarPistaForm, ContactoForm
from django.conf import settings
EMAIL_HOST_USER = settings.EMAIL_HOST_USER




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
        try:
            # Obtener el Cliente asociado al User actual
            cliente = Cliente.objects.get(user=self.request.user)
            return Reserva.objects.filter(cliente=cliente).order_by('-fecha', 'hora')
        except Cliente.DoesNotExist:
            # Si no existe Cliente para este User
            return Reserva.objects.none()


# -------------------------
# Vistas de Pistas
# -------------------------
class ListaPistasView(LoginRequiredMixin, ThemeMixin, ListView):

    model = Pista
    template_name = "bowl/cositas_admin/lista_pistas.html"
    context_object_name = "pistas"


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Esto asegura que pasamos todas las pistas
        context['pistas'] = Pista.objects.all()
        return context




class CrearPistaView(LoginRequiredMixin, ThemeMixin, CreateView):

    model = Pista
    form_class = CrearPistaForm
    template_name = "bowl/cositas_admin/crear_pistas.html"
    success_url = reverse_lazy('lista_pistas')  # adonde redirige después de crear

class EditarPistaView(LoginRequiredMixin, ThemeMixin, UpdateView):
    model = Pista
    form_class = EditarPistaForm
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
        return render(request, self.template_name)

    def post(self, request):
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        mensaje_texto = request.POST.get('mensaje')
        
        # Crear el mensaje del correo
        asunto = f'Nuevo mensaje de contacto de {nombre}'
        cuerpo = f"""
        Nombre: {nombre}
        Email: {email}
        
        Mensaje:
        {mensaje_texto}
        
        ---
        Enviado desde Space Bowling
        """
        
        try:
            print("🔄 Intentando enviar correo...")
            print(f"De: {EMAIL_HOST_USER}")
            print(f"Para: {EMAIL_HOST_USER}")
            print(f"Asunto: {asunto}")
            
            # Enviar el correo
            send_mail(
                asunto,
                cuerpo,
                EMAIL_HOST_USER,  # Desde
                [EMAIL_HOST_USER],  # Para
                fail_silently=False,
            )
            
            print("✅ Correo enviado exitosamente")
            messages.success(request, '¡Mensaje enviado correctamente! Te responderemos a la brevedad.')
            return redirect('contacto')
            
        except Exception as e:
            print(f"❌ ERROR al enviar correo: {str(e)}")
            messages.error(request, f'Error al enviar el mensaje. Por favor, intenta nuevamente. Error: {str(e)}')
            return redirect('contacto')