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

from .models import (
    Reserva, Pista, Cafeteria, Usuario, Cliente, TipoPista, Estado,
    Comida, Partida, Jugador, PuntajeJugador
)
from .forms import (
    PistaForm, CafeteriaForm, CrearPistaForm, EditarPistaForm,
    ContactoForm, MenuForm, RegistroUsuarioForm, ReservaForm,
    PuntajeForm, JugadorForm
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
    login_url = reverse_lazy('iniciar_sesion')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()

        # Horarios 14:00 - 23:00 cada 15 min
        h_inicio, h_fin = time(14, 0), time(23, 0)
        hora = datetime.combine(today, h_inicio)
        horarios = []
        while hora <= datetime.combine(today, h_fin):
            horarios.append(hora.strftime("%H:%M"))
            hora += timedelta(minutes=15)

        # Crea pistas por defecto si faltan
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

        fecha = self.request.GET.get('fecha')
        hora_sel = self.request.GET.get('hora')

        if fecha and hora_sel:
            try:
                fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
                hora_obj = datetime.strptime(hora_sel, '%H:%M').time()
                ocupadas = Reserva.objects.filter(fecha=fecha_obj, hora=hora_obj).values_list('pista_id', flat=True)
                pistas = Pista.objects.exclude(id__in=ocupadas)
            except:
                pistas = Pista.objects.all()
        else:
            pistas = Pista.objects.all()

        context.update({
            "today": today,
            "horarios": horarios,
            "pistas": pistas
        })
        return context

    def form_valid(self, form):
        user = self.request.user
        cliente = getattr(user, "cliente", None)

        if not cliente:
            messages.error(self.request, "No tienes un cliente asociado.")
            return redirect('reserva')

        form.instance.cliente = cliente
        form.instance.usuario = user

        try:
            form.instance.estado = Estado.objects.get(nombre="Pendiente")
            form.instance.precio_total = form.instance.pista.tipo_pista.precio
        except:
            messages.error(self.request, "Error al asignar estado o precio.")
            return redirect('nueva_reserva1')

        conflicto = Reserva.objects.filter(
            pista=form.instance.pista,
            fecha=form.instance.fecha,
            hora=form.instance.hora
        ).exists()

        if conflicto:
            messages.error(self.request, "La pista ya está reservada en ese horario.")
            return redirect('nueva_reserva1')

        messages.success(self.request, "Reserva creada correctamente.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, f"Error en el formulario: {form.errors}")
        return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse_lazy('reserva')


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


# ---------------------------------------------------------
# Cafetería
# ---------------------------------------------------------

class ListaComidaView(UsuarioContext, View):
    def get(self, request):
        comidas = Comida.objects.all()
        return render(request, "bowl/cositas_admin/lista_comidas.html", {"comidas": comidas})


class CrearComidaView(UsuarioContext, View):
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


# ---------------------------------------------------------
# Tablero de puntuaciones
# ---------------------------------------------------------

class TableroPuntuacionesView(LoginRequiredMixin, TemplateView):
    template_name = "bowl/tabla_puntuaciones.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        pk = self.kwargs.get('pk')
        reserva_actual = get_object_or_404(Reserva, pk=pk)
        
        partida, _ = Partida.objects.get_or_create(
            reserva=reserva_actual,
            defaults={'cliente': self.request.user.cliente, 'pista': reserva_actual.pista}
        )

        jugadores_puntajes = []

        for jugador in Jugador.objects.filter(partida=partida):
            puntajes = [
                PuntajeJugador.objects.get_or_create(
                    partida=partida, jugador=jugador, set=i, defaults={'puntaje': 0}
                )[0]
                for i in range(1, 11)
            ]

            jugadores_puntajes.append({
                'id': jugador.id_jugador,
                'nombre': jugador.nombre,
                'puntajes': [{'id_puntaje': p.id_puntaje, 'valor': p.puntaje} for p in puntajes],
                'total': sum(p.puntaje for p in puntajes)
            })

        context.update({
            'jugadores_puntajes': jugadores_puntajes,
            'partida_id': partida.id_partida,
            'jugador_form': JugadorForm()
        })

        return context

    def post(self, request, *args, **kwargs):
        return (
            self.agregar_jugador(request)
            if 'agregar_jugador' in request.POST
            else self.guardar_puntajes(request)
        )

    def agregar_jugador(self, request):
        try:
            cliente = Cliente.objects.get(user=request.user)
            reserva_actual = Reserva.objects.filter(cliente=cliente).order_by('-fecha').first()
            partida, _ = Partida.objects.get_or_create(
                reserva=reserva_actual,
                defaults={'cliente': cliente, 'pista': reserva_actual.pista}
            )

            form = JugadorForm(request.POST)
            if form.is_valid():
                jugador = form.save(commit=False)
                jugador.partida = partida
                jugador.save()

                for i in range(1, 11):
                    PuntajeJugador.objects.create(
                        partida=partida, jugador=jugador, set=i, puntaje=0
                    )

                messages.success(request, f"Jugador {jugador.nombre} agregado correctamente.")
            else:
                messages.error(request, "Error al agregar jugador.")

        except Exception as e:
            messages.error(request, f"Error: {e}")

        return redirect('tablero_puntuaciones')

    def guardar_puntajes(self, request):
        for key, value in request.POST.items():
            if key.startswith('puntaje-') and '-puntaje' in key:
                try:
                    puntaje_id = int(key.split('-')[1])
                    puntaje = get_object_or_404(PuntajeJugador, id_puntaje=puntaje_id)

                    if puntaje.partida.cliente.user == request.user:
                        puntaje.puntaje = max(0, min(int(value or 0), 300))
                        puntaje.save()
                except:
                    continue

        messages.success(request, "Puntajes guardados correctamente.")
        return redirect('tablero_puntuaciones')


# ---------------------------------------------------------
# Asignar admin
# ---------------------------------------------------------

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

        # Pedido actual de la reserva (si existe)
        pedido = getattr(reserva_activa, 'pedido', None)
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