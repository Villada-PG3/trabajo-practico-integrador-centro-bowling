from django.contrib import admin
from .models import Pista, Cliente, Reserva, Partida, Jugador, Turno, Menu, Pedido

@admin.register(Pista)
class PistaAdmin(admin.ModelAdmin):
    list_display = ('id_pista', 'capacidad_maxima')
    search_fields = ('id_pista',)


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('id_cliente', 'nombre', 'direccion', 'telefono', 'email')
    search_fields = ('nombre', 'email')


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('id_reserva', 'fecha', 'hora', 'cliente', 'pista', 'estado')
    list_filter = ('estado', 'fecha')
    search_fields = ('id_reserva',)


@admin.register(Partida)
class PartidaAdmin(admin.ModelAdmin):
    list_display = ('id_partida', 'pista', 'reserva')


@admin.register(Jugador)
class JugadorAdmin(admin.ModelAdmin):
    list_display = ('id_jugador', 'nombre')
    search_fields = ('nombre',)


@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ('id_turno', 'numero_turno', 'partida', 'jugador')
    list_filter = ('partida', 'jugador')


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('id_menu', 'nombre', 'precio')
    search_fields = ('nombre',)


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id_pedido', 'horario', 'precio_total', 'reserva', 'menu')
    list_filter = ('horario',)
