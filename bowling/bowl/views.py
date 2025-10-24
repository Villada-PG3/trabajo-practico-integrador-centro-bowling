# bowl/views.py
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import TemplateView, ListView, CreateView, UpdateView
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from datetime import datetime, time, timedelta
from .models import Reserva, Pista, Cafeteria, Usuario
from .forms import PistaForm, CafeteriaForm, CrearPistaForm, EditarPistaForm, ReservaForm

from django.core.mail import send_mail
from .models import Reserva, Pista, Cafeteria, Mensaje, Cliente, Menu, comida, Estado
from .forms import PistaForm, CafeteriaForm, CrearPistaForm, EditarPistaForm, ContactoForm, MenuForm, RegistroUsuarioForm, ReservaForm
from django.shortcuts import render
from django.utils import timezone

class ThemeMixin:
    """Agrega theme_mode al contexto de todas las vistas que lo usen"""
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['theme_mode'] = self.request.session.get('theme_mode','light')
# ---------- Vistas de Inicio y Tema ----------
class InicioView(TemplateView):
    template_name = "bowl/inicio.html"


from django.conf import settings
EMAIL_HOST_USER = settings.EMAIL_HOST_USER

from django.views.generic import TemplateView

class GaleriaView(TemplateView):
    template_name = "bowl/galeria.html"

class ReglasView(TemplateView):
    template_name = "bowl/reglas.html"

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
        if self.request.user.is_authenticated:
            context["Usuario"] = self.request.user
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


def nosotros(request):
    return render(request, 'bowl/nosotros.html')


# -------------------------
# Vistas de Reservas
# -------------------------
# Vista para mostrar tus reservas
class ReservaListView(LoginRequiredMixin, ThemeMixin, ListView):
    """Página principal: muestra tus reservas y botón de nueva reserva"""
    model = Reserva
    template_name = 'bowl/reserva.html'
    context_object_name = 'reservas'
    login_url = '/login/'

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


class ReservaCreateView(LoginRequiredMixin, ThemeMixin, CreateView):
    """Formulario para crear nueva reserva"""
    model = Reserva
    form_class = ReservaForm
    template_name = 'bowl/nueva_reserva1.html'
    login_url = '/login/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()

        # Horarios válidos: 14:00 → 23:00
        hora_inicio = time(14, 0)
        hora_fin = time(23, 0)
        horarios = []
        hora_actual = datetime.combine(today, hora_inicio)
        hora_fin_dt = datetime.combine(today, hora_fin)

        while hora_actual <= hora_fin_dt:
            horarios.append(hora_actual.strftime("%H:%M"))
            hora_actual += timedelta(minutes=15)

        # Crear pistas base si faltan
        if Pista.objects.count() < 10:
            tipo_normal, _ = TipoPista.objects.get_or_create(
                tipo="Normal", defaults={'zona': 'General', 'precio': 10000}
            )
            tipo_vip, _ = TipoPista.objects.get_or_create(
                tipo="VIP", defaults={'zona': 'VIP', 'precio': 15000}
            )
            tipo_ultra, _ = TipoPista.objects.get_or_create(
                tipo="UltraVIP", defaults={'zona': 'Ultra', 'precio': 20000}
            )

            for i in range(1, 5):
                Pista.objects.get_or_create(numero=i, defaults={'tipo_pista': tipo_normal})
            for i in range(5, 8):
                Pista.objects.get_or_create(numero=i, defaults={'tipo_pista': tipo_vip})
            for i in range(8, 11):
                Pista.objects.get_or_create(numero=i, defaults={'tipo_pista': tipo_ultra})


        # Pistas disponibles según fecha/hora seleccionadas
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

        context['today'] = today
        context['horarios'] = horarios
        context['pistas'] = pistas_disponibles
        return context

    def form_valid(self, form):
        user = self.request.user
        try:
            cliente = user.cliente
        except Cliente.DoesNotExist:
            messages.error(self.request, "No tienes un cliente asociado.")
            return redirect('reserva')

        form.instance.cliente = cliente
        form.instance.usuario = user
        form.instance.estado = Estado.objects.get(nombre="Pendiente")
        form.instance.precio_total = form.instance.pista.tipo_pista.precio  # ✅ corregido

        # Evita conflictos de horario
        if Reserva.objects.filter(
            pista=form.instance.pista,
            fecha=form.instance.fecha,
            hora=form.instance.hora
        ).exists():
            messages.error(self.request, "Esta pista ya está reservada en ese horario.")
            return redirect('nueva_reserva1')

        messages.success(self.request, "Reserva creada correctamente.")
        return super().form_valid(form)


    def get_success_url(self):
        return reverse_lazy('reserva')
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
class ListaComidaView(View):
    def get(self, request):
        comidas = comida.objects.all()
        return render(request, "bowl/cositas_admin/lista_comidas.html", {"comidas": comidas})

class CrearComidaView(View):
    def get(self, request):
        form = MenuForm()
        return render(request, "bowl/cositas_admin/crear_comida.html", {"form": form})

    def post(self, request):
        form = MenuForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("lista_comida")
        return render(request, "bowl/cositas_admin/crear_comida.html", {"form": form})
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


class AsignarAdminView(LoginRequiredMixin, ThemeMixin, View):
    template_name = "bowl/cositas_admin/asignar_admin.html"


    def get(self, request):
        # Solo los usuarios con rol 'admin' pueden acceder
        if getattr(request.user, 'rol', None) != 'admin':
            messages.error(request, "No tienes permiso para acceder a esta página.")
           # return redirect('inicio')

        usuarios = Usuario.objects.all().order_by('username')
        return render(request, self.template_name, {'usuarios': usuarios})

    def post(self, request):
        # Solo los usuarios con rol 'admin' pueden cambiar roles
        if getattr(request.user, 'rol', None) != 'admin':
            messages.error(request, "No tienes permiso para realizar esta acción.")
            return redirect('inicio')

        user_id = request.POST.get('user_id')
        nuevo_rol = request.POST.get('rol')

        try:
            usuario = Usuario.objects.get(id=user_id)
            usuario.rol = nuevo_rol
            usuario.save()
            messages.success(request, f"✅ El rol de {usuario.username} se actualizó correctamente.")
        except Usuario.DoesNotExist:
            messages.error(request, "❌ Usuario no encontrado.")

        return redirect('asignar_admin')
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
        

def registro(request):
    if request.method == "POST":
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Usuario {user.username} registrado correctamente")
            return render(request, "bowl/inicio_sesion1.html")
        else:
            # Esto muestra los errores reales del form
            print(form.errors)
            messages.error(request, "Hubo un error en el formulario")
    else:
        form = RegistroUsuarioForm()
    return render(request, "bowl/registro.html", {"form": form})