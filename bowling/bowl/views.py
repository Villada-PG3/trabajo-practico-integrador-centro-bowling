# bowl/views.py

from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from django.views.generic import TemplateView, ListView, CreateView, UpdateView
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, time, timedelta
from django.core.serializers import serialize
from django.db.models import Sum
from django.db import models    
import json

from .models import (
    Reserva, Pista, Cafeteria, Usuario, Cliente, TipoPista, Estado,
     Partida, Jugador, Frame, PuntajeJugador
)
from .forms import (
    CrearPistaForm, EditarPistaForm,
    ContactoForm, RegistroUsuarioForm, ReservaForm,
     JugadorForm
)

EMAIL_HOST_USER = settings.EMAIL_HOST_USER

# ---------------------------------------------------------
# Mixins
# ---------------------------------------------------------

class ThemeMixin:
    """Agrega modo oscuro/claro al contexto."""
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['theme_mode'] = self.request.session.get('theme_mode', 'light')
        return context


class UsuarioContext:
    """Agrega usuario y rol al contexto."""
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context['usuario'] = user if user.is_authenticated else None
        context['Usuario'] = getattr(user, 'rol', '') == 'admin'
        return context


# ---------------------------------------------------------
# Inicio y páginas informativas
# ---------------------------------------------------------

class InicioView(ThemeMixin, UsuarioContext, TemplateView):
    template_name = "bowl/inicio.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['estado_logueo'] = 0
        return context

class CafeView(LoginRequiredMixin, ThemeMixin, UsuarioContext, TemplateView):
    template_name = "bowl/cafe.html"


class LoginnView(ThemeMixin, UsuarioContext, LoginView):
    template_name = "bowl/inicio_sesion1.html"

def toggle_theme_mode(request):
    modo_actual = request.session.get('theme_mode', 'light')
    request.session['theme_mode'] = 'dark' if modo_actual == 'light' else 'light'
    return redirect(request.META.get('HTTP_REFERER', 'inicio'))


# ---------------------------------------------------------
# Reservas
# ---------------------------------------------------------

class ReservaListView(LoginRequiredMixin, ThemeMixin, UsuarioContext, ListView):
    model = Reserva
    template_name = 'bowl/reserva.html'
    context_object_name = 'reservas'
    login_url = reverse_lazy('iniciar_sesion')

    def get_queryset(self):
        user = self.request.user
        cliente = getattr(user, "cliente", None)
        if not cliente:
            return Reserva.objects.none()

        # Solo mostrar reservas que aún están pendientes (es decir, activas)
        return Reserva.objects.filter(
            cliente=cliente,
            estado__nombre="Pendiente"       # ¡Solo las pendientes!
        ).order_by('-fecha', '-hora')
    
class ReservaCreateView(LoginRequiredMixin, ThemeMixin, UsuarioContext, CreateView):
    model = Reserva
    form_class = ReservaForm
    template_name = 'bowl/nueva_reserva1.html'
    success_url = reverse_lazy('reserva')
    login_url = reverse_lazy('iniciar_sesion')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()

        # === Generar horarios cada 1 hora: 14:00 a 23:00 ===
        horarios = []
        for hora in range(14, 24):  # 14 a 23 inclusive
            horarios.append(f"{hora:02d}:00")

        # === Crear pistas por defecto si no existen ===
        if Pista.objects.count() < 10:
            tipo_normal, _ = TipoPista.objects.get_or_create(tipo="Normal", defaults={'zona': 'General', 'precio': 10000})
            tipo_vip, _ = TipoPista.objects.get_or_create(tipo="VIP", defaults={'zona': 'VIP', 'precio': 15000})
            tipo_ultra, _ = TipoPista.objects.get_or_create(tipo="UltraVIP", defaults={'zona': 'Ultra', 'precio': 20000})

            for i in range(1, 5):
                Pista.objects.get_or_create(numero=i, defaults={'tipo_pista': tipo_normal})
            for i in range(5, 8):
                Pista.objects.get_or_create(numero=i, defaults={'tipo_pista': tipo_vip})
            for i in range(8, 11):
                Pista.objects.get_or_create(numero=i, defaults={'tipo_pista': tipo_ultra})

        # === Fecha seleccionada (por GET o hoy por defecto) ===
        fecha_str = self.request.GET.get('fecha')
        if fecha_str:
            try:
                fecha_seleccionada = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            except ValueError:
                fecha_seleccionada = today
        else:
            fecha_seleccionada = today

        # === Obtener disponibilidad para el día seleccionado ===
        horarios_disponibilidad = []
        for hora_str in horarios:
            hora = datetime.strptime(hora_str, '%H:%M').time()
            
            # IDs de pistas YA RESERVADAS en ese horario (estado "Pendiente", case-insensitive)
            ocupadas_ids = Reserva.objects.filter(
                fecha=fecha_seleccionada,
                hora=hora,
                estado__nombre__iexact="Pendiente"
            ).values_list('pista_id', flat=True)

            # Excluir por la PK real de Pista (el modelo Pista tiene primary_key=id_pista)
            # pero .pk funciona igual; ocupadas_ids contiene ints que comparan bien
            pistas_disponibles_qs = Pista.objects.exclude(id_pista__in=ocupadas_ids)

            # Construimos un JSON simple con los campos que necesitamos en el cliente (JS)
            pistas_simple = []
            for p in pistas_disponibles_qs:
                pistas_simple.append({
                    'pk': p.pk,
                    'numero': p.numero,
                    'tipo': p.tipo_pista.tipo if p.tipo_pista else None,
                    'precio': p.tipo_pista.precio if p.tipo_pista else None,
                })

            horarios_disponibilidad.append({
                'hora': hora_str,
                'disponible': pistas_disponibles_qs.exists(),
                'pistas': pistas_disponibles_qs,
                'cantidad': pistas_disponibles_qs.count(),
                # pasamos string JSON ya listo para el template (evita repr de Python)
                'pistas_json': json.dumps(pistas_simple, ensure_ascii=False, default=str),
            })

        context.update({
            'horarios': horarios,
            'horarios_disponibilidad': horarios_disponibilidad,
            'fecha_seleccionada': fecha_seleccionada,
            'today': today,
            'pistas_totales': Pista.objects.all(),
        })
       
        return context

    def form_valid(self, form):
        user = self.request.user
        # Obtener el cliente asociado (más robusto que getattr)
        try:
            cliente = Cliente.objects.get(user=user)
        except Cliente.DoesNotExist:
            cliente = None

        if not cliente:
            messages.error(self.request, "No tienes un perfil de cliente asociado.")
            return redirect('nueva_reserva1')

        # Validar que la pista y horario estén libres
        pista = form.cleaned_data.get('pista')
        fecha = form.cleaned_data.get('fecha')
        hora = form.cleaned_data.get('hora')

        if not pista or not fecha or not hora:
            messages.error(self.request, "Faltan datos para crear la reserva.")
            return redirect('nueva_reserva1')

        conflicto = Reserva.objects.filter(
            pista=pista,
            fecha=fecha,
            hora=hora,
            estado__nombre__iexact="Pendiente"
        ).exists()

        if conflicto:
            messages.error(self.request, "Esta pista ya está reservada en ese horario.")
            return redirect('nueva_reserva1')

        # Rellenamos campos necesarios antes de guardar
        form.instance.cliente = cliente
        form.instance.usuario = user
        # Asegúrate de que exista el Estado "Pendiente" en la BD
        estado_pendiente, _ = Estado.objects.get_or_create(nombre="Pendiente")
        form.instance.estado = estado_pendiente
        # precio desde tipo_pista
        if pista.tipo_pista:
            form.instance.precio_total = pista.tipo_pista.precio
        else:
            form.instance.precio_total = 0.0

        messages.success(self.request, f"Reserva creada para el {fecha} a las {hora.strftime('%H:%M')} en pista {pista.numero}.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Por favor corrige los errores del formulario.")
        return self.render_to_response(self.get_context_data(form=form))
# ---------------------------------------------------------
# Pistas
# ---------------------------------------------------------

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

# views.py → TableroPuntuacionesView (versión definitiva y probada)
# bowl/views.py → TableroPuntuacionesView (VERSIÓN BOLERA REAL)






class TableroPuntuacionesView(LoginRequiredMixin, TemplateView):
    template_name = "bowl/tabla_puntuaciones.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get('pk')
        reserva = get_object_or_404(Reserva, pk=pk)

        # === CREACIÓN DE PARTIDA + JUGADOR DEL CLIENTE AUTOMÁTICO ===
        partida, creada = Partida.objects.get_or_create(
            reserva=reserva,
            defaults={
                'cliente': self.request.user.cliente,
                'pista': reserva.pista
            }
        )

        # Si la partida es nueva → creamos automáticamente al cliente como jugador
        if creada:
            nombre_jugador = self.request.user.get_full_name() or self.request.user.username
            jugador_cliente, _ = Jugador.objects.get_or_create(
                partida=partida,
                nombre=nombre_jugador,
            )

            # Creamos los 10 frames vacíos para este jugador
            for frame in range(1, 11):
                PuntajeJugador.objects.create(
                    partida=partida,
                    jugador=jugador_cliente,
                    set=frame,
                    puntaje=0
                )

        clave = f'partida_iniciada_{partida.id_partida}'
        partida_iniciada = self.request.session.get(clave, False)

        # === JUGADORES Y PUNTAJES ===
        jugadores = Jugador.objects.filter(partida=partida).order_by('id_jugador')
        jugadores_puntajes = []

        for jugador in jugadores:
            puntajes = []
            for frame in range(1, 11):
                p, _ = PuntajeJugador.objects.get_or_create(
                    partida=partida,
                    jugador=jugador,
                    set=frame,
                    defaults={'puntaje': 0}
                )
                puntajes.append({
                    'frame': frame,
                    'puntaje': p.puntaje,
                    'es_actual': False
                })

            total = sum(item['puntaje'] for item in puntajes)

            jugadores_puntajes.append({
                'id': jugador.id_jugador,
                'nombre': jugador.nombre,
                'puntajes': puntajes,
                'total': total,
                'es_turno_actual': False,
            })

        # === LÓGICA DE TURNO + DETECCIÓN DE PARTIDA TERMINADA (CORREGIDA) ===
        jugador_actual = None
        frame_actual = 1
        partida_terminada = False

        # Buscamos el primer tiro pendiente (puntaje = 0)
        siguiente_turno_db = PuntajeJugador.objects.filter(
            partida=partida,
            puntaje=0
        ).order_by('set', 'jugador__id_jugador').first()

        if siguiente_turno_db:
            # Hay tiros por jugar
            frame_actual = siguiente_turno_db.set
            for j in jugadores_puntajes:
                if j['id'] == siguiente_turno_db.jugador.id_jugador:
                    jugador_actual = j
                    j['es_turno_actual'] = True
                    for p in j['puntajes']:
                        if p['frame'] == frame_actual:
                            p['es_actual'] = True
                            break
                    break

        else:
            # NO hay tiros pendientes → ¿la partida realmente terminó?
            # Solo es "terminada" si además ya se presionó "Empezar partida"
            if partida_iniciada and jugadores_puntajes:
                partida_terminada = True
                frame_actual = 10
            else:
                # Caso: hay jugadores pero nadie empezó todavía
                partida_terminada = False
                frame_actual = 1

        # Ganador SOLO si la partida está terminada y fue iniciada
        ganador = None
        if partida_terminada and jugadores_puntajes:
            ganador = max(jugadores_puntajes, key=lambda x: x['total'])

        # === CONTEXTO FINAL ===
        context.update({
            'reserva': reserva,
            'jugadores_puntajes': jugadores_puntajes,
            'partida_iniciada': partida_iniciada,
            'frame_actual': frame_actual,
            'jugador_actual': jugador_actual or {'nombre': '—'},
            'partida_terminada': partida_terminada,
            'ganador': ganador,
            'reserva_pk': pk,
            'jugador_form': JugadorForm(),
        })
        return context

    def post(self, request, *args, **kwargs):
        if 'empezar_partida' in request.POST:
            return self.empezar_partida(request)
        if 'agregar_jugador' in request.POST:
            return self.agregar_jugador(request)
        if 'registrar_turno' in request.POST:
            return self.registrar_turno_real(request)
        return redirect('tablero_puntuaciones', pk=self.kwargs['pk'])

    def empezar_partida(self, request):
        pk = self.kwargs.get('pk')
        partida = Partida.objects.get(reserva__pk=pk)
        request.session[f'partida_iniciada_{partida.id_partida}'] = True
        messages.success(request, "PARTIDA INICIADA – ¡A tirar bolos!")
        return redirect('tablero_puntuaciones', pk=pk)

    def agregar_jugador(self, request):
        pk = self.kwargs.get('pk')
        reserva = get_object_or_404(Reserva, pk=pk)
        partida = Partida.objects.get(reserva=reserva)

        if request.session.get(f'partida_iniciada_{partida.id_partida}', False):
            messages.error(request, "No se pueden agregar jugadores una vez empezada la partida")
            return redirect('tablero_puntuaciones', pk=pk)

        form = JugadorForm(request.POST)
        if form.is_valid():
            jugador = form.save(commit=False)
            jugador.partida = partida
            jugador.save()
            for i in range(1, 11):
                PuntajeJugador.objects.create(partida=partida, jugador=jugador, set=i, puntaje=0)
            messages.success(request, f"{jugador.nombre} agregado")
        return redirect('tablero_puntuaciones', pk=pk)

    def registrar_turno_real(self, request):
        pk = self.kwargs.get('pk')
        reserva = get_object_or_404(Reserva, pk=pk)
        partida = Partida.objects.get(reserva=reserva)

        # Usamos .get() en lugar de .get('puntaje_turno', 0) or 0, para asegurar que el 0 pase.
        try:
            puntaje = int(request.POST.get('puntaje_turno', 0)) 
        except ValueError:
            puntaje = 0
            
        puntaje = max(0, min(10, puntaje)) # Máximo 10 pinos por tiro (Simplificación)

        # Encontrar el TURNO ACTUAL pendiente
        turno = PuntajeJugador.objects.filter(
            partida=partida,
            puntaje=0
        ).order_by('set', 'jugador__id_jugador').first()

        # Si hay turno → guardar tiro
        if turno:
            turno.puntaje = puntaje
            turno.save()
            messages.success(request, f"Frame {turno.set} → {turno.jugador.nombre}: {puntaje} puntos")

        # AHORA: comprobar si ya no quedan tiros (Partida Terminada)
        quedan_tiros = PuntajeJugador.objects.filter(partida=partida, puntaje=0).exists()

        if not quedan_tiros:
            # PARTIDA TERMINADA
            try:
                # Nota: Asegúrate de que 'Estado' y 'Completada' existan en tus models
                estado_completada = Estado.objects.get(nombre="Completada") 
            except Estado.DoesNotExist:
                messages.error(request, "Error: No existe el estado 'Completada'")
                return redirect('tablero_puntuaciones', pk=pk)

            reserva.estado = estado_completada
            reserva.fecha_completada = timezone.now()
            reserva.save()

            # El cálculo del ganador se hace en el GET, pero repetimos el mensaje de éxito
            # para que aparezca al momento de finalizar el último tiro.
            messages.success(request, f"¡PARTIDA TERMINADA!")

        return redirect('tablero_puntuaciones', pk=pk)



class AsignarAdminView(LoginRequiredMixin, ThemeMixin, UsuarioContext, View):
    template_name = "bowl/cositas_admin/asignar_admin.html"

    def get(self, request):
        if getattr(request.user, 'rol', None) != 'admin':
            messages.error(request, "No tienes permiso para acceder.")
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
            messages.success(request, f"Rol de {usuario.username} cambiado correctamente.")
        except Usuario.DoesNotExist:
            messages.error(request, "Usuario no encontrado.")

        return redirect('asignar')


# ---------------------------------------------------------
# Contacto
# ---------------------------------------------------------

class ContactoView(UsuarioContext, View):
    template_name = "bowl/contactos.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        nombre = request.POST.get('nombre')
        email = request.POST.get('email')
        mensaje = request.POST.get('mensaje')

        asunto = f'Nuevo mensaje de {nombre}'
        cuerpo = f"""
        Nombre: {nombre}
        Email: {email}

        Mensaje:
        {mensaje}
        -- Enviado desde Space Bowling
        """

        try:
            send_mail(asunto, cuerpo, EMAIL_HOST_USER, [EMAIL_HOST_USER])
            messages.success(request, "Mensaje enviado correctamente.")
        except Exception as e:
            messages.error(request, f"Error al enviar: {e}")

        return redirect('contacto')


# ---------------------------------------------------------
# Registro
# ---------------------------------------------------------

def registro(request):
    if request.method == "POST":
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Usuario {user.username} registrado correctamente.")
            return render(request, "bowl/inicio_sesion1.html")
        messages.error(request, "Error en el formulario.")
    else:
        form = RegistroUsuarioForm()

    return render(request, "bowl/registro.html", {"form": form})



# ---------------------------------------------------------
# Página de gestión de reserva activa
# ---------------------------------------------------------

class GestionReservaView(LoginRequiredMixin, ThemeMixin, UsuarioContext, TemplateView):
    template_name = "bowl/gestion_reserva.html"
    login_url = reverse_lazy('iniciar_sesion')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get('pk')
        context[pk] = pk
        hoy = timezone.now().date()
        ahora = timezone.now().time()

        user = self.request.user
        cliente = getattr(user, "cliente", None)
        



        reserva_activa = get_object_or_404(Reserva, pk=pk)

        if not reserva_activa:
            context['reserva_activa'] = None
            return context

        # Calculamos si ya puede entrar (15 min antes)
        hora_inicio = (datetime.combine(hoy, reserva_activa.hora) - timedelta(hours=1)).time()
        puede_entrar = ahora >= hora_inicio
        puede_entrar = True
        # Pedido actual de la reserva (si existe)
        pedido = getattr(reserva_activa, 'pedido', None)
        context['puede_entrar'] = puede_entrar
        print(reserva_activa)
        context["reserva"] = reserva_activa

        return context

    def post(self, request, *args, **kwargs):
        accion = request.POST.get('accion')
        print("Accion recibida:", accion)
        if accion == "cancelar":
            return self.cancelar_reserva(request, pk=self.kwargs.get('pk'))
        elif accion == "agregar_comida":
            return self.agregar_comida_reserva(request)
        
        return redirect('reserva')

    def cancelar_reserva(self, request, pk):
        reserva_id = request.POST.get('reserva_id')
        reserva = get_object_or_404(Reserva, id_reserva=pk)
        print("Intentando cancelar reserva:", reserva)    
        # Regla: solo se puede cancelar con más de 2 horas de antelación
        fecha_hora_reserva = timezone.make_aware(
            datetime.combine(reserva.fecha, reserva.hora)
        )
    


        estado_disponible = Estado.objects.get(nombre="Disponible")
        reserva.estado = estado_disponible
        reserva.save()
        print("Reserva cancelada:", reserva)
        messages.success(request, "Reserva cancelada y pista liberada correctamente.")
        
        return redirect('reserva')  # va a la lista de reservas activas

    def agregar_comida_reserva(self, request):
        reserva_id = request.POST.get('reserva_id')
        comida_id = request.POST.get('comida_id')
        cantidad = int(request.POST.get('cantidad', 1))

        reserva = get_object_or_404(Reserva, id=reserva_id, cliente=request.user.cliente)
        comida = get_object_or_404(Comida, id=comida_id)

        # Creamos o obtenemos el pedido de la reserva
        pedido, _ = Pedido.objects.get_or_create(reserva=reserva)

        # Añadimos la comida (puedes usar through model si tienes cantidad, aquí simplificado)
        pedido.comidas.add(comida)  # Si tienes modelo Pedido tiene ManyToMany directo
        # Si tienes un modelo intermedio con cantidad, cambia la lógica aquí

        messages.success(request, f"{comida.nombre} ×{cantidad} añadido al pedido.")
        return redirect('gestion_reserva')