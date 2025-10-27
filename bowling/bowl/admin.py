from django.contrib import admin
from .models import (
    Jugador, EstadisticasJugador, Pista, TipoPista, Usuario, Reserva, Estado,
    Partida, Turno, JugadorPartida, Cafeteria, Menu, Pedido, DetallePedido, Cliente, Comida, Mensaje, PuntajeJugador
)

# === ADMIN DE JUGADOR ===
@admin.register(Jugador)
class JugadorAdmin(admin.ModelAdmin):
    list_display = ('id_jugador', 'nombre', 'get_cliente', 'get_cliente_email')
    search_fields = ('nombre', 'partida__cliente__email')

    # Cliente a través de la partida
    def get_cliente(self, obj):
        return obj.partida.cliente.nombre if obj.partida and obj.partida.cliente else "-"
    get_cliente.short_description = "Cliente"

    def get_cliente_email(self, obj):
        return obj.partida.cliente.email if obj.partida and obj.partida.cliente else "-"
    get_cliente_email.short_description = "Email"

# === ADMIN DE ESTADÍSTICAS DE JUGADOR ===
@admin.register(EstadisticasJugador)
class EstadisticasJugadorAdmin(admin.ModelAdmin):
    list_display = ('id_estadistica', 'jugador', 'partidas_jugadas', 'promedio_puntaje', 'total_strikes', 'total_spares')
    search_fields = ('jugador__nombre',)

# === ADMIN DE PISTA ===
@admin.register(Pista)
class PistaAdmin(admin.ModelAdmin):
    list_display = ('id_pista', 'numero', 'capacidad_maxima', 'estado', 'tipo_pista')
    search_fields = ('numero',)

# === ADMIN DE ESTADO ===
@admin.register(Estado)
class EstadoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)

# === ADMIN DE COMIDA ===
@admin.register(Comida)
class ComidaAdmin(admin.ModelAdmin):
    list_display = ('id_comida', 'nombre', 'descripcion', 'precio')
    search_fields = ('nombre',)

# === ADMIN DE TIPO DE PISTA ===
@admin.register(TipoPista)
class TipoPistaAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo', 'zona', 'precio', 'descuento', 'descripcion')

    def has_add_permission(self, request):
        if TipoPista.objects.count() >= 3:
            return False
        return True

# === ADMIN DE CLIENTE ===
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('id_cliente', 'nombre', 'direccion', 'telefono', 'email')
    search_fields = ('nombre', 'email')

# === ADMIN DE RESERVA ===
@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('id_reserva', 'fecha', 'hora', 'cliente', 'pista', 'precio_total', 'estado', 'usuario')
    list_filter = ('fecha', 'estado', 'cliente')
    search_fields = ('id_reserva', 'cliente__nombre', 'pista__numero')

# === ADMIN DE PARTIDA ===
@admin.register(Partida)
class PartidaAdmin(admin.ModelAdmin):
    list_display = ('id_partida', 'cliente', 'pista', 'reserva', 'duracion', 'puntaje_final')

# === ADMIN DE JUGADORPARTIDA ===
@admin.register(JugadorPartida)
class JugadorPartidaAdmin(admin.ModelAdmin):
    list_display = ('id_jugador_partida', 'jugador', 'partida', 'puntaje_final', 'posicion')

# === ADMIN DE TURNO ===
@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = (
        'id_turno', 'numero_turno', 'partida', 'jugador_partida', 'lanzamiento1', 'lanzamiento2',
        'lanzamiento3', 'puntaje_turno', 'bonus', 'strike', 'spare',
        'falta1', 'falta2', 'falta3', 'frame_final'
    )
    list_filter = ('partida', 'jugador_partida')

# === ADMIN DE CAFETERÍA ===
@admin.register(Cafeteria)
class CafeteriaAdmin(admin.ModelAdmin):
    list_display = ('id_cafeteria', 'nombre', 'horario_apertura', 'horario_cierre')

    def has_add_permission(self, request):
        if Cafeteria.objects.exists():
            return False
        return True

# === ADMIN DE MENÚ ===
@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('id_menu', 'nombre', 'descripcion', 'precio')
    search_fields = ('nombre',)

# === ADMIN DE PEDIDO ===
@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id_pedido', 'horario', 'precio_total', 'reserva', 'cafeteria', 'cliente')
    list_filter = ('horario',)

# === ADMIN DE DETALLE PEDIDO ===
@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ('id_detalle_pedido', 'pedido', 'menu', 'cliente', 'cantidad', 'subtotal')

# === ADMIN DE MENSAJE ===
@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'fecha')

# === ADMIN DE PUNTAJE JUGADOR ===
@admin.register(PuntajeJugador)
class PuntajeJugadorAdmin(admin.ModelAdmin):
    list_display = ('id_puntaje', 'jugador', 'partida', 'puntaje', 'set')
