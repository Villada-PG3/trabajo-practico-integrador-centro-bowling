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
from .models import Menu, Pedido, DetallePedido
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
# Inicio y pÃ¡ginas informativas
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

        # Solo mostrar reservas que aÃºn estÃ¡n pendientes (es decir, activas)
        return Reserva.objects.filter(
            cliente=cliente,
            estado__nombre="Pendiente"       # Â¡Solo las pendientes!
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

        # === Obtener disponibilidad para el dÃ­a seleccionado ===
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
        # Obtener el cliente asociado (mÃ¡s robusto que getattr)
        try:
            cliente = Cliente.objects.get(user=user)
        except Cliente.DoesNotExist:
            cliente = None

        if not cliente:
            messages.error(self.request, "No tienes un perfil de cliente asociado.")
            return redirect('nueva_reserva1')

        # Validar que la pista y horario estÃ©n libres
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
            messages.error(self.request, "Esta pista ya estÃ¡ reservada en ese horario.")
            return redirect('nueva_reserva1')

        # Rellenamos campos necesarios antes de guardar
        form.instance.cliente = cliente
        form.instance.usuario = user
        # AsegÃºrate de que exista el Estado "Pendiente" en la BD
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











class TableroPuntuacionesView(LoginRequiredMixin, TemplateView):
    template_name = "bowl/tabla_puntuaciones.html"

    def _asegurar_frames(self, partida):
        """Crea frames vacíos para todos los jugadores si no existen."""
        jugadores = Jugador.objects.filter(partida=partida)
        for jugador in jugadores:
            for numero in range(1, 11):
                Frame.objects.get_or_create(jugador=jugador, numero=numero)

    def _siguiente_tiro(self, partida):
        """
        Devuelve el siguiente tiro pendiente.
        Retorna dict con: jugador, frame, tiro (1/2/3), maximo permitido.
        """
        jugadores = Jugador.objects.filter(partida=partida).order_by('id_jugador')
        for numero in range(1, 11):
            for jugador in jugadores:
                frame = Frame.objects.get(jugador=jugador, numero=numero)

                # Tiro 1 siempre pendiente si no está hecho
                if frame.tiro1 is None:
                    return {'jugador': jugador, 'frame': frame, 'tiro': 1, 'maximo': 10}

                # Frames 1-9
                if numero < 10:
                    if frame.tiro1 < 10 and frame.tiro2 is None:
                        return {'jugador': jugador, 'frame': frame, 'tiro': 2, 'maximo': 10 - frame.tiro1}

                # Frame 10 - lógica especial
                else:
                    if frame.tiro2 is None:
                        max_tiro2 = 10 if frame.tiro1 == 10 else (10 - frame.tiro1)
                        return {'jugador': jugador, 'frame': frame, 'tiro': 2, 'maximo': max_tiro2}

                    if (frame.tiro1 == 10 or (frame.tiro1 + frame.tiro2) >= 10) and frame.tiro3 is None:
                        if frame.tiro1 == 10 and frame.tiro2 == 10:
                            max_tiro3 = 10
                        elif frame.tiro1 == 10:
                            max_tiro3 = 10 - frame.tiro2
                        else:
                            max_tiro3 = 10
                        return {'jugador': jugador, 'frame': frame, 'tiro': 3, 'maximo': max_tiro3}

        return None  # Partida terminada

    def _formatear_frame(self, frame):
        """Devuelve X, /, números o guiones para mostrar en la tabla."""
        t1, t2, t3 = frame.tiro1, frame.tiro2, frame.tiro3

        if frame.numero < 10:
            if t1 is None:
                return "-"
            if t1 == 10:
                return "X"
            if t2 is None:
                return f"{t1} -"
            if t1 + t2 >= 10:
                return f"{t1} /"
            return f"{t1} {t2}"

        # Frame 10
        partes = []

        # Tiro 1
        if t1 == 10:
            partes.append("X")
        elif t1 is None:
            partes.append("-")
        else:
            partes.append(str(t1))

        # Tiro 2
        if t2 is None:
            partes.append("-")
        elif t1 == 10 and t2 == 10:
            partes.append("X")
        elif t1 != 10 and t1 + t2 >= 10:
            partes.append("/")
        else:
            partes.append(str(t2))

        # Tiro 3 (solo si existe)
        if t3 is not None:
            if t3 == 10:
                partes.append("X")
            elif (t1 == 10 or t1 + t2 >= 10) and (t2 + t3 >= 10) and t2 != 10:
                partes.append("/")
            else:
                partes.append(str(t3))

        return " ".join(partes) if partes else "-"

    def _calcular_puntaje_acumulado(self, jugador):
        """
        CÁLCULO OFICIAL DE BOWLING.
        Devuelve lista de 10 frames con puntaje acumulado correcto.
        """
        frames = list(Frame.objects.filter(jugador=jugador).order_by('numero'))
        resultado = []
        total = 0

        for i, frame in enumerate(frames):
            t1 = frame.tiro1 or 0
            t2 = frame.tiro2 or 0
            t3 = frame.tiro3 or 0 if frame.numero == 10 else 0

            if frame.numero < 10:
                if t1 == 10:  # Strike
                    # Próximos 2 tiros
                    if i + 1 < 10:
                        next1 = frames[i + 1]
                        bonus1 = next1.tiro1 or 0
                        bonus2 = (next1.tiro2 or 0) if next1.tiro1 != 10 or i + 2 >= 10 else (frames[i + 2].tiro1 or 0)
                    else:  # frame 9 → frame 10
                        bonus1 = frames[9].tiro2 or 0
                        bonus2 = frames[9].tiro3 or 0
                    puntaje_frame = 10 + bonus1 + bonus2

                elif t1 + t2 == 10:  # Spare
                    bonus = frames[i + 1].tiro1 or 0 if i + 1 < 10 else (frames[9].tiro2 or 0)
                    puntaje_frame = 10 + bonus

                else:
                    puntaje_frame = t1 + t2

            else:  # Frame 10 → sin bonus, se suman los 3 tiros tal cual
                puntaje_frame = t1 + t2 + t3

            total += puntaje_frame
            resultado.append({
                'frame_numero': frame.numero,
                'puntaje_frame': puntaje_frame,
                'puntaje_acumulado': total,
                'display': self._formatear_frame(frame),
                'frame_obj': frame,
            })

        return resultado, total

    def _armar_tabla(self, partida):
        turno = self._siguiente_tiro(partida)
        jugadores = Jugador.objects.filter(partida=partida).order_by('id_jugador')
        tabla = []

        for jugador in jugadores:
            puntajes_frames, total_final = self._calcular_puntaje_acumulado(jugador)

            # Marcar cuál es el frame/tiro actual del jugador
            for item in puntajes_frames:
                es_actual = (
                    turno and
                    item['frame_obj'].id == turno['frame'].id and
                    turno['jugador'].id_jugador == jugador.id_jugador
                )
                item['es_actual'] = es_actual

            tabla.append({
                'id': jugador.id_jugador,
                'nombre': jugador.nombre,
                'puntajes': puntajes_frames,
                'total': total_final,
                'es_turno_actual': turno and turno['jugador'].id_jugador == jugador.id_jugador,
            })

        frame_actual = turno['frame'].numero if turno else 1
        jugador_actual = turno['jugador'] if turno else None
        tiro_actual = turno['tiro'] if turno else 1
        maximo_tiro = turno['maximo'] if turno else 10

        return tabla, frame_actual, jugador_actual, tiro_actual, maximo_tiro

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get('pk')
        reserva = get_object_or_404(Reserva, pk=pk)

        partida, creada = Partida.objects.get_or_create(
            reserva=reserva,
            defaults={'cliente': self.request.user.cliente, 'pista': reserva.pista}
        )

        if creada:
            nombre = self.request.user.get_full_name() or self.request.user.username
            jugador, _ = Jugador.objects.get_or_create(partida=partida, nombre=nombre)

        self._asegurar_frames(partida)

        clave_sesion = f'partida_iniciada_{partida.id_partida}'
        partida_iniciada = self.request.session.get(clave_sesion, False)

        jugadores_puntajes, frame_actual, jugador_actual, tiro_actual, maximo_tiro = self._armar_tabla(partida)
        partida_terminada = partida_iniciada and not self._siguiente_tiro(partida)

        ganador = None
        if partida_terminada and jugadores_puntajes:
            ganador = max(jugadores_puntajes, key=lambda x: x['total'])

        context.update({
            'reserva': reserva,
            'jugadores_puntajes': jugadores_puntajes,
            'partida_iniciada': partida_iniciada,
            'frame_actual': frame_actual,
            'jugador_actual': jugador_actual or {'nombre': '--'},
            'tiro_actual': tiro_actual,
            'tiro_maximo': maximo_tiro,
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
        messages.success(request, "PARTIDA INICIADA - ¡A tirar bolos!")
        return redirect('tablero_puntuaciones', pk=pk)

    def agregar_jugador(self, request):
        pk = self.kwargs.get('pk')
        reserva = get_object_or_404(Reserva, pk=pk)
        partida = Partida.objects.get(reserva=reserva)

        if self.request.session.get(f'partida_iniciada_{partida.id_partida}', False):
            messages.error(request, "No se pueden agregar jugadores una vez iniciada la partida")
            return redirect('tablero_puntuaciones', pk=pk)

        form = JugadorForm(request.POST)
        if form.is_valid():
            jugador = form.save(commit=False)
            jugador.partida = partida
            jugador.save()
            for i in range(1, 11):
                Frame.objects.get_or_create(jugador=jugador, numero=i)
            messages.success(request, f"{jugador.nombre} agregado a la partida")
        return redirect('tablero_puntuaciones', pk=pk)

    def registrar_turno_real(self, request):
        pk = self.kwargs.get('pk')
        reserva = get_object_or_404(Reserva, pk=pk)
        partida = Partida.objects.get(reserva=reserva)
        turno = self._siguiente_tiro(partida)

        if not turno:
            messages.info(request, "La partida ya terminó.")
            return redirect('tablero_puntuaciones', pk=pk)

        try:
            pins = int(request.POST.get('puntaje_turno', 0))
        except ValueError:
            pins = 0

        pins = max(0, min(pins, turno['maximo']))
        frame = turno['frame']

        if turno['tiro'] == 1:
            frame.tiro1 = pins
            if frame.numero < 10 and pins == 10:
                frame.tiro2 = 0  # Strike en 1-9 → segundo tiro no se juega
        elif turno['tiro'] == 2:
            frame.tiro2 = pins
        else:  # tiro 3 (solo frame 10)
            frame.tiro3 = pins

        frame.save()

        marca = self._formatear_frame(frame)
        messages.success(request, f"{turno['jugador'].nombre} - Frame {frame.numero}: {marca}")

        # Si no quedan más tiros → partida terminada
        if not self._siguiente_tiro(partida):
            try:
                estado_completada = Estado.objects.get(nombre="Completada")
                reserva.estado = estado_completada
                reserva.fecha_completada = timezone.now()
                reserva.save()
            except Estado.DoesNotExist:
                pass  # opcional: crear el estado si no existe
            messages.success(request, "PARTIDA TERMINADA - ¡Felicitaciones a todos!")

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
            messages.error(request, "No tienes permiso para realizar esta acciÃ³n.")
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
# PÃ¡gina de gestiÃ³n de reserva activa
# ---------------------------------------------------------
class GestionReservaView(LoginRequiredMixin, ThemeMixin, UsuarioContext, TemplateView):
    template_name = "bowl/gestion_reserva.html"
    login_url = reverse_lazy('iniciar_sesion')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get('pk')
        reserva = get_object_or_404(Reserva, pk=pk, cliente=self.request.user.cliente)

        # Crear o obtener el pedido asociado a la reserva
        pedido, _ = Pedido.objects.get_or_create(
            reserva=reserva,
            defaults={'cliente': self.request.user.cliente}
        )

        # Detalles del pedido con menú relacionado
        detalles = DetallePedido.objects.filter(pedido=pedido).select_related('menu')

        # Calcular total del pedido
        total_pedido = sum(detalle.subtotal or 0 for detalle in detalles)

        # Menú disponible
        menu_items = Menu.objects.filter(disponible=True)

        # Lógica de "puede entrar" (mantiene tu lógica original + mejora)
        hoy = timezone.now().date()
        ahora = timezone.now().time()
        hora_permitida = (datetime.combine(hoy, reserva.hora) - timedelta(hours=1)).time()
        puede_entrar = (reserva.fecha < hoy) or (reserva.fecha == hoy and ahora >= hora_permitida)

        context.update({
            'reserva': reserva,
            'pedido': pedido,
            'detalles_pedido': detalles,
            'total_pedido': total_pedido,
            'menu_items': menu_items,
            'puede_entrar': puede_entrar,
        })
        return context
    def post(self, request, *args, **kwargs):
        accion = request.POST.get('accion')
        pk = self.kwargs.get('pk')
        reserva = get_object_or_404(Reserva, pk=pk, cliente=request.user.cliente)

        if accion == "cancelar":
            return self.cancelar_reserva(request, reserva)
        elif accion == "agregar_comida":
            return self.agregar_comida_reserva(request, reserva)
        elif accion == "enviar_pedido":
            return self.enviar_pedido(request, reserva)

        return redirect('gestion_reserva', pk=pk)

    def enviar_pedido(self, request, reserva):
        pedido = Pedido.objects.get(reserva=reserva)
        if not pedido.detalles.exists():
            messages.warning(request, "¡Agregá algo antes de enviar el pedido!")
            return redirect('gestion_reserva', pk=reserva.pk)

        # Usa el estado que YA existe en tu base de datos
        estado_cocina = Estado.objects.get(nombre="En preparación")
        pedido.estado = estado_cocina
        pedido.save()
        
        messages.success(request, "¡Pedido enviado a cocina! En breve te lo llevan a la pista.")
        return redirect('gestion_reserva', pk=reserva.pk)

    def cancelar_reserva(self, request, reserva):
        # Tu lógica original de cancelación (corregida)
        try:
            estado_disponible = Estado.objects.get(nombre="Disponible")
        except Estado.DoesNotExist:
            estado_disponible = Estado.objects.create(nombre="Disponible")
        
        reserva.estado = estado_disponible
        reserva.save()
        messages.success(request, "Reserva cancelada y pista liberada correctamente.")
        return redirect('reserva')

    def agregar_comida_reserva(self, request, reserva):
        menu_id = request.POST.get('menu_id')
        cantidad_str = request.POST.get('cantidad', '1')
        
        try:
            cantidad = int(cantidad_str)
            if cantidad < 1:
                raise ValueError
        except ValueError:
            messages.error(request, "Cantidad inválida.")
            return redirect('gestion_reserva', pk=reserva.pk)

        if not menu_id:
            messages.error(request, "Debes seleccionar un producto.")
            return redirect('gestion_reserva', pk=reserva.pk)

        menu = get_object_or_404(Menu, id=menu_id, disponible=True)
        pedido = Pedido.objects.get(reserva=reserva)

        # Buscar si ya existe el detalle para sumar cantidad
        detalle, creado = DetallePedido.objects.get_or_create(
            pedido=pedido,
            menu=menu,
            defaults={'cantidad': cantidad}
        )
        if not creado:
            detalle.cantidad += cantidad
            detalle.save()  # El save() recalcula el subtotal gracias al método save() del modelo

        # Recalcular precio_total del pedido
        pedido.precio_total = sum(d.subtotal or 0 for d in pedido.detalles.all())
        pedido.save()

        messages.success(request, f"Agregado: {cantidad} × {menu.nombre}")
        return redirect('gestion_reserva', pk=reserva.pk)