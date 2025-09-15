from django.contrib import admin
from .models import (
    Jugador, EstadisticasJugador, Pista, TipoPista, Usuario, Reserva,
    Partida, Turno, JugadorPartida, Cafeteria, Menu, Pedido, DetallePedido, Cliente
)

@admin.register(Jugador)
class JugadorAdmin(admin.ModelAdmin):
    list_display = ('id_jugador', 'nombre', 'edad', 'email')
    search_fields = ('nombre', 'email')

@admin.register(EstadisticasJugador)
class EstadisticasJugadorAdmin(admin.ModelAdmin):
    list_display = ('id_estadistica', 'jugador', 'partidas_jugadas', 'promedio_puntaje', 'total_strikes', 'total_spares')
    search_fields = ('jugador__nombre',)

@admin.register(Pista)
class PistaAdmin(admin.ModelAdmin):
    list_display = ('id_pista', 'capacidad_maxima', 'estado', 'tipo_pista')
    search_fields = ('id_pista',)

@admin.register(TipoPista)
class TipoPistaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'zona', 'precio', 'descuento', 'descripcion')
    search_fields = ('nombre',)

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'nombre_usuario', 'email', 'activo')
    search_fields = ('nombre_usuario', 'email')

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('id_cliente', 'nombre', 'direccion', 'telefono', 'email')
    search_fields = ('nombre', 'email')

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('id_reserva', 'fecha', 'hora', 'cliente', 'pista', 'estado', 'precio_total')
    list_filter = ('estado', 'fecha')
    search_fields = ('id_reserva',)

@admin.register(Partida)
class PartidaAdmin(admin.ModelAdmin):
    list_display = ('id_partida', 'pista', 'reserva', 'duracion')

@admin.register(JugadorPartida)
class JugadorPartidaAdmin(admin.ModelAdmin):
    list_display = ('id', 'jugador', 'partida', 'puntaje_final', 'posicion')

@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = (
        'id_turno', 'numero_turno', 'partida', 'jugador', 'lanzamiento1', 'lanzamiento2', 
        'lanzamiento3', 'puntaje_turno', 'bonus', 'strike', 'spare', 
        'falta1', 'falta2', 'falta3', 'frame_final'
    )
    list_filter = ('partida', 'jugador')

@admin.register(Cafeteria)
class CafeteriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'ubicacion', 'horario_apertura', 'horario_cierre', 'capacidad_maxima', 'email', 'telefono')
    search_fields = ('nombre',)

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('id_menu', 'nombre', 'descripcion', 'precio')
    search_fields = ('nombre',)

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id_pedido', 'horario', 'precio_total', 'reserva', 'menu')
    list_filter = ('horario',)

@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ('id_detalle_pedido', 'pedido', 'menu', 'cliente', 'cantidad', 'subtotal')
