# bowl/views.py
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import TemplateView, ListView, CreateView, UpdateView
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from datetime import datetime, time, timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

# Importación de modelos y formularios
from .models import Reserva, Pista, Cafeteria, Usuario, Cliente, TipoPista, Estado, comida
from .forms import (
    PistaForm, CafeteriaForm, CrearPistaForm, EditarPistaForm,
    ContactoForm, MenuForm, RegistroUsuarioForm, ReservaForm
)

EMAIL_HOST_USER = settings.EMAIL_HOST_USER

# -------------------------
# Mixins: clases reutilizables para compartir lógica entre vistas
# -------------------------
class ThemeMixin:
    """Agrega el modo de tema (oscuro/claro) al contexto"""
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['theme_mode'] = self.request.session.get('theme_mode', 'light')
        return context


class UsuarioContext:
    """Agrega información del usuario y su rol al contexto"""
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request
        if hasattr(request, 'user') and getattr(request.user, 'is_authenticated', False):
            context['usuario'] = request.user
            context['Usuario'] = getattr(request.user, 'rol', '') == 'admin'
        else:
            context['usuario'] = None
            context['Usuario'] = False
        return context

# -------------------------
# Vistas de Inicio y Tema
# -------------------------
class InicioView(ThemeMixin, UsuarioContext, TemplateView):
    template_name = "bowl/inicio.html"
    # Agrega información del usuario al contexto de la página principal
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['estado_logueo'] = 0
        if self.request.user.is_authenticated:
            context["Usuario"] = self.request.user
        return context

# Vistas informativas simples
class GaleriaView(ThemeMixin, UsuarioContext, TemplateView):
    template_name = "bowl/galeria.html"

class ReglasView(ThemeMixin, UsuarioContext, TemplateView):
    template_name = "bowl/reglas.html"

class CafeView(LoginRequiredMixin, ThemeMixin, UsuarioContext, TemplateView):
    template_name = "bowl/cafe.html"

class LoginnView(ThemeMixin, UsuarioContext, LoginView):
    template_name = "bowl/inicio_sesion1.html"

# Página estática sin clases
def nosotros(request):
    return render(request, 'bowl/nosotros.html')

def toggle_theme_mode(request):
    """Alterna entre modo claro y oscuro"""
    current_mode = request.session.get('theme_mode', 'light')
    request.session['theme_mode'] = 'dark' if current_mode == 'light' else 'light'
    return redirect(request.META.get('HTTP_REFERER', 'inicio'))

# -------------------------
# Vistas de Reservas
# -------------------------
class ReservaListView(LoginRequiredMixin, ThemeMixin, UsuarioContext, ListView):
    """Lista las reservas del cliente autenticado"""
    model = Reserva
    template_name = 'bowl/reserva.html'
    context_object_name = 'reservas'
    login_url = reverse_lazy('iniciar_sesion')

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            cliente = getattr(user, "cliente", None)
            if cliente:
                return Reserva.objects.filter(cliente=cliente).order_by('-fecha', '-hora')
        return Reserva.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today'] = timezone.now().date()
        return context


class ReservaCreateView(LoginRequiredMixin, ThemeMixin, UsuarioContext, CreateView):
    """Permite crear una nueva reserva"""
    model = Reserva
    form_class = ReservaForm
    template_name = 'bowl/nueva_reserva1.html'
    login_url = reverse_lazy('iniciar_sesion')

    def get_context_data(self, **kwargs):
        """Prepara horarios disponibles y pistas libres"""
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()

        # Genera una lista de horarios cada 15 minutos entre 14:00 y 23:00
        hora_inicio, hora_fin = time(14, 0), time(23, 0)
        horarios = []
        hora_actual = datetime.combine(today, hora_inicio)
        while hora_actual <= datetime.combine(today, hora_fin):
            horarios.append(hora_actual.strftime("%H:%M"))
            hora_actual += timedelta(minutes=15)

        # Crea pistas por defecto si no existen
        if Pista.objects.count() < 10:
            tipo_normal, _ = TipoPista.objects.get_or_create(
                tipo="Normal", defaults={'zona': 'General', 'precio': 10000})
            tipo_vip, _ = TipoPista.objects.get_or_create(
                tipo="VIP", defaults={'zona': 'VIP', 'precio': 15000})
            tipo_ultra, _ = TipoPista.objects.get_or_create(
                tipo="UltraVIP", defaults={'zona': 'Ultra', 'precio': 20000})
            for i in range(1, 5):
                Pista.objects.get_or_create(numero=i, defaults={'tipo_pista': tipo_normal})
            for i in range(5, 8):
                Pista.objects.get_or_create(numero=i, defaults={'tipo_pista': tipo_vip})
            for i in range(8, 11):
                Pista.objects.get_or_create(numero=i, defaults={'tipo_pista': tipo_ultra})

        # Filtra las pistas disponibles según fecha y hora
        fecha = self.request.GET.get('fecha')
        hora = self.request.GET.get('hora')
        if fecha and hora:
            try:
                fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
                hora_obj = datetime.strptime(hora, '%H:%M').time()
                ocupadas = Reserva.objects.filter(fecha=fecha_obj, hora=hora_obj).values_list('pista_id', flat=True)
                pistas_disponibles = Pista.objects.exclude(id__in=ocupadas)
            except ValueError:
                pistas_disponibles = Pista.objects.all()
        else:
            pistas_disponibles = Pista.objects.all()

        context.update({
            'today': today,
            'horarios': horarios,
            'pistas': pistas_disponibles
        })
        return context

    def form_valid(self, form):
        """Guarda la reserva asociándola al usuario y cliente"""
        user = self.request.user
        try:
            cliente = user.cliente
        except Cliente.DoesNotExist:
            messages.error(self.request, "No tienes un cliente asociado.")
            return redirect('reserva')

        form.instance.cliente = cliente
        form.instance.usuario = user

        # Asigna estado y precio
        try:
            form.instance.estado = Estado.objects.get(nombre="Pendiente")
            form.instance.precio_total = form.instance.pista.tipo_pista.precio
        except Exception:
            messages.error(self.request, "Error al asignar estado o tipo de pista.")
            return redirect('nueva_reserva1')

        # Verifica conflictos de horario
        if Reserva.objects.filter(
            pista=form.instance.pista,
            fecha=form.instance.fecha,
            hora=form.instance.hora
        ).exists():
            messages.error(self.request, "Esta pista ya está reservada en ese horario.")
            return redirect('nueva_reserva1')

        messages.success(self.request, "Reserva creada correctamente.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, f"Error en el formulario: {form.errors}")
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse_lazy('reserva')

# -------------------------
# Vistas de Pistas
# -------------------------
class ListaPistasView(LoginRequiredMixin, ThemeMixin, UsuarioContext, ListView):
    model = Pista
    template_name = "bowl/cositas_admin/lista_pistas.html"
    context_object_name = "pistas"

class CrearPistaView(LoginRequiredMixin, ThemeMixin, UsuarioContext, CreateView):
    model = Pista
    form_class = CrearPistaForm
    template_name = "bowl/cositas_admin/crear_pistas.html"
    success_url = reverse_lazy('lista_pistas')

class EditarPistaView(LoginRequiredMixin, ThemeMixin, UsuarioContext, UpdateView):
    model = Pista
    form_class = EditarPistaForm
    template_name = "bowl/cositas_admin/editar_pistas.html"
    success_url = reverse_lazy('lista_pistas')

# -------------------------
# Vistas de Cafetería
# -------------------------
class ListaComidaView(UsuarioContext, View):
    """Lista los productos de la cafetería"""
    def get(self, request):
        comidas = comida.objects.all()
        return render(request, "bowl/cositas_admin/lista_comidas.html", {"comidas": comidas})

class CrearComidaView(UsuarioContext, View):
    """Crea nuevos productos de comida"""
    def get(self, request):
        return render(request, "bowl/cositas_admin/crear_comida.html", {"form": MenuForm()})
    def post(self, request):
        form = MenuForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("lista_comida")
        return render(request, "bowl/cositas_admin/crear_comida.html", {"form": form})

class CrearCafeteriaView(LoginRequiredMixin, ThemeMixin, UsuarioContext, CreateView):
    model = Cafeteria
    form_class = CafeteriaForm
    template_name = "bowl/cositas_admin/crear_comida.html"
    success_url = reverse_lazy('lista_comida')

class EditarCafeteriaView(LoginRequiredMixin, ThemeMixin, UsuarioContext, UpdateView):
    model = Cafeteria
    form_class = CafeteriaForm
    template_name = "bowl/cositas_admin/editar_comida.html"
    success_url = reverse_lazy('lista_comida')

class AsignarAdminView(LoginRequiredMixin, ThemeMixin, UsuarioContext, View):
    """Permite asignar o cambiar el rol de los usuarios"""
    template_name = "bowl/cositas_admin/asignar_admin.html"

    def get(self, request):
        if getattr(request.user, 'rol', None) != 'admin':
            messages.error(request, "No tienes permiso para acceder a esta página.")
            return redirect('inicio')
        usuarios = Usuario.objects.all().order_by('username')
        return render(request, self.template_name, {'usuarios': usuarios})

    def post(self, request):
        if getattr(request.user, 'rol', None) != 'admin':
            messages.error(request, "No tienes permiso para realizar esta acción.")
            return redirect('inicio')

        user_id = request.POST.get('user_id')
        nuevo_rol = request.POST.get('rol')

        try:
            usuario = Usuario.objects.get(id=user_id)
            usuario.rol = nuevo_rol
            usuario.save()
            messages.success(request, f"✅ Rol de {usuario.username} actualizado correctamente.")
        except Usuario.DoesNotExist:
            messages.error(request, "❌ Usuario no encontrado.")

        return redirect('asignar')

# -------------------------
# Vista de Contacto
# -------------------------
class ContactoView(UsuarioContext, View):
    """Envía un mensaje al correo del administrador"""
    template_name = "bowl/contactos.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        mensaje_texto = request.POST.get('mensaje')

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
            send_mail(asunto, cuerpo, EMAIL_HOST_USER, [EMAIL_HOST_USER], fail_silently=False)
            messages.success(request, '¡Mensaje enviado correctamente!')
        except Exception as e:
            messages.error(request, f'Error al enviar el mensaje: {str(e)}')
        return redirect('contacto')

# -------------------------
# Vista de Registro
# -------------------------
def registro(request):
    """Permite crear un nuevo usuario desde un formulario"""
    if request.method == "POST":
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Usuario {user.username} registrado correctamente")
            return render(request, "bowl/inicio_sesion1.html")
        messages.error(request, "Hubo un error en el formulario")
    else:
        form = RegistroUsuarioForm()
    return render(request, "bowl/registro.html", {"form": form})
