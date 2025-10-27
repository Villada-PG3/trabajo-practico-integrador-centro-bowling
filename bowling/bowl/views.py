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

from .models import Reserva, Pista, Cafeteria, Usuario, Cliente, TipoPista, Estado, Comida, Partida,Jugador, PuntajeJugador
from .forms import (
    PistaForm, CafeteriaForm, CrearPistaForm, EditarPistaForm,
    ContactoForm, MenuForm, RegistroUsuarioForm, ReservaForm, PuntajeForm
)

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

class UsuarioContext:
    """Agrega 'usuario' y 'Usuario' al contexto de todas las vistas que lo usen"""
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['estado_logueo'] = 0
        if self.request.user.is_authenticated:
            context["Usuario"] = self.request.user
        return context

class GaleriaView(ThemeMixin, UsuarioContext, TemplateView):
    template_name = "bowl/galeria.html"

class ReglasView(ThemeMixin, UsuarioContext, TemplateView):
    template_name = "bowl/reglas.html"

class CafeView(LoginRequiredMixin, ThemeMixin, UsuarioContext, TemplateView):
    template_name = "bowl/cafe.html"

class LoginnView(ThemeMixin, UsuarioContext, LoginView):
    template_name = "bowl/inicio_sesion1.html"

def nosotros(request):
    return render(request, 'bowl/nosotros.html')

def toggle_theme_mode(request):
    """Alterna entre light y dark"""
    current_mode = request.session.get('theme_mode', 'light')
    request.session['theme_mode'] = 'dark' if current_mode == 'light' else 'light'
    return redirect(request.META.get('HTTP_REFERER', 'inicio'))

# -------------------------
# Vistas de Reservas
# -------------------------
class ReservaListView(LoginRequiredMixin, ThemeMixin, UsuarioContext, ListView):
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
    model = Reserva
    form_class = ReservaForm
    template_name = 'bowl/nueva_reserva1.html'
    login_url = reverse_lazy('iniciar_sesion')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        hora_inicio = time(14, 0)
        hora_fin = time(23, 0)
        horarios = []
        hora_actual = datetime.combine(today, hora_inicio)
        hora_fin_dt = datetime.combine(today, hora_fin)
        while hora_actual <= hora_fin_dt:
            horarios.append(hora_actual.strftime("%H:%M"))
            hora_actual += timedelta(minutes=15)

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
        print("Form:", form)       
        print("Form cleaned data:", form.cleaned_data)
        user = self.request.user
        try:
            cliente = user.cliente
        except Cliente.DoesNotExist:
            print("No cliente associated with user:", user.username)
            messages.error(self.request, "No tienes un cliente asociado.")
            return redirect('reserva')

        form.instance.cliente = cliente
        form.instance.usuario = user
        try:
            form.instance.estado = Estado.objects.get(nombre="Pendiente")
        except Estado.DoesNotExist:
            print("Estado 'Pendiente' not found")
            messages.error(self.request, "Error: Estado 'Pendiente' no encontrado.")
            return redirect('nueva_reserva1')

        try:
            form.instance.precio_total = form.instance.pista.tipo_pista.precio
        except AttributeError:
            print("Invalid pista or tipo_pista")
            messages.error(self.request, "Error: Pista inválida o sin tipo asociado.")
            return redirect('nueva_reserva1')

        # Conflict check is already in clean(), but keep for safety
        if Reserva.objects.filter(
            pista=form.instance.pista,
            fecha=form.instance.fecha,
            hora=form.instance.hora
        ).exists():
            print("Conflict detected for pista:", form.instance.pista, "fecha:", form.instance.fecha, "hora:", form.instance.hora)
            messages.error(self.request, "Esta pista ya está reservada en ese horario.")
            return redirect('nueva_reserva1')

        messages.success(self.request, "Reserva creada correctamente.")
        return super().form_valid(form)

    def form_invalid(self, form):
        print("Form errors:", form.errors)
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pistas'] = Pista.objects.all()
        return context

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
    def get(self, request):
        comidas = Comida.objects.all()
        return render(request, "bowl/cositas_admin/lista_comidas.html", {"comidas": comidas})

class CrearComidaView(UsuarioContext, View):
    def get(self, request):
        form = MenuForm()
        return render(request, "bowl/cositas_admin/crear_comida.html", {"form": form})

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

# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from .models import Cliente, Reserva, Partida, Jugador, PuntajeJugador
from .forms import PuntajeForm, JugadorForm

class TableroPuntuacionesView(LoginRequiredMixin, TemplateView):
    template_name = "bowl/tabla_puntuaciones.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            cliente = Cliente.objects.get(user=self.request.user)
        except Cliente.DoesNotExist:
            context['jugadores_puntajes'] = []
            context['partida_id'] = None
            context['jugador_form'] = JugadorForm()
            return context

        reservas = Reserva.objects.filter(cliente=cliente).order_by('-fecha', '-hora')
        if reservas.exists():
            reserva_actual = reservas[0]
            partida = Partida.objects.filter(reserva=reserva_actual).last()
            
            if partida is None:
                partida = Partida.objects.create(
                    cliente=cliente,
                    pista=reserva_actual.pista,
                    reserva=reserva_actual
                )

            jugadores_puntajes = []
            jugadores = Jugador.objects.filter(partida=partida)

            for jugador in jugadores:
                # Obtener o crear puntajes para cada set
                puntajes_data = []
                for set_num in range(1, 11):
                    puntaje_obj, created = PuntajeJugador.objects.get_or_create(
                        partida=partida,
                        jugador=jugador,
                        set=set_num,
                        defaults={'puntaje': 0}
                    )
                    puntajes_data.append({
                        'id_puntaje': puntaje_obj.id_puntaje,
                        'valor': puntaje_obj.puntaje,
                    })
                
                total = sum(p['valor'] for p in puntajes_data)
                
                jugadores_puntajes.append({
                    'id': jugador.id_jugador,
                    'nombre': jugador.nombre,
                    'puntajes': puntajes_data,
                    'total': total
                })

            context['jugadores_puntajes'] = jugadores_puntajes
            context['partida_id'] = partida.id_partida
            context['jugador_form'] = JugadorForm()
        else:
            context['jugadores_puntajes'] = []
            context['partida_id'] = None
            context['jugador_form'] = JugadorForm()

        return context

    def post(self, request, *args, **kwargs):
        # Verificar si es para agregar jugador o guardar puntajes
        if 'agregar_jugador' in request.POST:
            # Procesar agregar jugador
            return self.agregar_jugador(request)
        else:
            # Procesar guardar puntajes
            return self.guardar_puntajes(request)

    def agregar_jugador(self, request):
        try:
            cliente = Cliente.objects.get(user=request.user)
            reservas = Reserva.objects.filter(cliente=cliente).order_by('-fecha', '-hora')
            
            if reservas.exists():
                reserva_actual = reservas[0]
                partida = Partida.objects.filter(reserva=reserva_actual).last()
                
                if partida is None:
                    partida = Partida.objects.create(
                        cliente=cliente,
                        pista=reserva_actual.pista,
                        reserva=reserva_actual
                    )

                form = JugadorForm(request.POST)
                if form.is_valid():
                    jugador = form.save(commit=False)
                    jugador.partida = partida
                    jugador.save()
                    
                    # Crear puntajes iniciales para el nuevo jugador
                    for set_num in range(1, 11):
                        PuntajeJugador.objects.create(
                            partida=partida,
                            jugador=jugador,
                            set=set_num,
                            puntaje=0
                        )
                    
                    messages.success(request, f'Jugador {jugador.nombre} agregado correctamente!')
                else:
                    messages.error(request, 'Error al agregar jugador. Verifica los datos.')
            
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
        
        return redirect('tablero_puntuaciones')

    def guardar_puntajes(self, request):
        # Procesar todos los forms de puntajes
        for key, value in request.POST.items():
            if key.startswith('puntaje-'):
                if '-puntaje' in key:
                    # Extraer el ID del puntaje del nombre del campo
                    try:
                        puntaje_id = key.split('-')[1]
                        puntaje_id = int(puntaje_id)
                        puntaje_obj = get_object_or_404(PuntajeJugador, id_puntaje=puntaje_id)
                        
                        # Verificar permisos
                        if puntaje_obj.partida.cliente.user == request.user:
                            nuevo_valor = int(value) if value else 0
                            if 0 <= nuevo_valor <= 300:
                                puntaje_obj.puntaje = nuevo_valor
                                puntaje_obj.save()
                    except (ValueError, PuntajeJugador.DoesNotExist):
                        continue
        
        messages.success(request, 'Puntajes guardados correctamente!')
        return redirect('tablero_puntuaciones')


class AsignarAdminView(LoginRequiredMixin, ThemeMixin, UsuarioContext, View):
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
            messages.success(request, f"✅ El rol de {usuario.username} se actualizó correctamente.")
        except Usuario.DoesNotExist:
            messages.error(request, "❌ Usuario no encontrado.")

        return redirect('asignar')

# -------------------------
# VISTA DE CONTACTO
# -------------------------
class ContactoView(UsuarioContext, View):
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
            send_mail(
                asunto,
                cuerpo,
                EMAIL_HOST_USER,
                [EMAIL_HOST_USER],
                fail_silently=False,
            )
            messages.success(request, '¡Mensaje enviado correctamente! Te responderemos a la brevedad.')
            return redirect('contacto')
        except Exception as e:
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
            print(form.errors)
            messages.error(request, "Hubo un error en el formulario")
    else:
        form = RegistroUsuarioForm()
    return render(request, "bowl/registro.html", {"form": form})


class NuevoJugadorView(LoginRequiredMixin, ThemeMixin, UsuarioContext, View):
    template_name = "bowl/nuevo_jugador.html"

    def get(self, request, partida_id):
        form = AgregarJugadorForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request, partida_id):
        form = AgregarJugadorForm(request.POST)
        if form.is_valid():
            nombre_jugador = form.cleaned_data['nombre_jugador']
            jugador = Jugador.objects.create(nombre=nombre_jugador, partida = partida_id)
            for set in range(1, 11):
                PuntajeJugador.objects.create(jugador=jugador, partida_id=partida_id, puntaje=0, set=set)
            
            messages.success(request, f"Jugador {jugador.nombre} agregado correctamente.")

            return redirect('lista_jugadores')
        return render(request, self.template_name, {"form": form})