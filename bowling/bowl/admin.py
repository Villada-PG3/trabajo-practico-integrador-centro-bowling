from django.contrib import admin
from .models import (
    Pista, TipoPista, Cliente, Usuario, Reserva, Partida, Jugador, 
    JugadorPartida, Turno, Menu, Pedido, DetallePedido, Cafeteria, 
    EstadisticasJugador
)

@admin.register(Pista)
class PistaAdmin(admin.ModelAdmin):
    list_display = ('id_pista', 'capacidad_maxima', 'estado', 'tipo_pista')
    search_fields = ('id_pista',)

@admin.register(TipoPista)
class TipoPistaAdmin(admin.ModelAdmin):
    list_display = ('id_tipo_pista', 'tipo', 'zona', 'precio', 'descuento')
    search_fields = ('tipo', 'zona')

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('id_cliente', 'nombre', 'direccion', 'telefono', 'email')
    search_fields = ('nombre', 'email')

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('id_usuario', 'cliente', 'nombre_usuario', 'email', 'fecha_creacion', 'activo')
    list_filter = ('activo', 'fecha_creacion')
    search_fields = ('nombre_usuario', 'email')

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('id_reserva', 'fecha', 'hora', 'usuario', 'pista', 'estado', 'precio_total')
    list_filter = ('estado', 'fecha')
    search_fields = ('id_reserva',)

@admin.register(Partida)
class PartidaAdmin(admin.ModelAdmin):
    list_display = ('id_partida', 'pista', 'reserva', 'duracion')

@admin.register(Jugador)
class JugadorAdmin(admin.ModelAdmin):
    list_display = ('id_jugador', 'nombre', 'edad', 'email')
    search_fields = ('nombre', 'email')

@admin.register(JugadorPartida)
class JugadorPartidaAdmin(admin.ModelAdmin):
    list_display = ('id_jugador_partida', 'jugador', 'partida', 'puntaje_final', 'posicion')

@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ('id_turno', 'numero_turno', 'partida', 'jugador', 'puntaje_turno', 'strike', 'spare')
    list_filter = ('partida', 'jugador')

@admin.register(EstadisticasJugador)
class EstadisticasJugadorAdmin(admin.ModelAdmin):
    list_display = ('id_estadistica', 'jugador', 'partidas_jugadas', 'promedio_puntaje', 'total_strikes', 'total_spares')

@admin.register(Cafeteria)
class CafeteriaAdmin(admin.ModelAdmin):
    list_display = ('id_cafeteria', 'nombre', 'ubicacion', 'horario_apertura', 'horario_cierre', 'capacidad_maxima')
    search_fields = ('nombre', 'ubicacion')

@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('id_menu', 'nombre', 'precio')
    search_fields = ('nombre',)

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id_pedido', 'horario', 'precio_total', 'reserva', 'cafeteria', 'cliente')
    list_filter = ('horario',)

@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ('id_detalle_pedido', 'pedido', 'menu', 'cantidad', 'subtotal')
