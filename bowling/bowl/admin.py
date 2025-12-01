# bowl/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Usuario, Cliente, Estado, TipoPista, Pista, Reserva,
    Partida, Jugador, Frame,
    Cafeteria, Menu, Pedido, DetallePedido, Mensaje
)


# ==============================================================================
# USUARIO Y CLIENTE
# ==============================================================================

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'email', 'rol', 'is_staff', 'date_joined')
    list_filter = ('rol', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')
    fieldsets = UserAdmin.fieldsets + (
        ('Rol en Bowling', {'fields': ('rol',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Rol', {'fields': ('rol',)}),
    )


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'user', 'email', 'telefono')
    search_fields = ('nombre', 'user__username', 'email')
    raw_id_fields = ('user',)


# ==============================================================================
# PISTAS Y TIPOS
# ==============================================================================

@admin.register(Estado)
class EstadoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)


@admin.register(TipoPista)
class TipoPistaAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'zona', 'precio', 'descuento')
    search_fields = ('tipo', 'zona')
    list_editable = ('precio', 'descuento')


@admin.register(Pista)
class PistaAdmin(admin.ModelAdmin):
    list_display = ('numero', 'tipo_pista', 'estado', 'capacidad_maxima')
    list_filter = ('tipo_pista', 'estado')
    search_fields = ('numero',)
    list_editable = ('estado',)


# ==============================================================================
# RESERVAS Y PARTIDAS
# ==============================================================================

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('id_reserva', 'cliente', 'pista', 'fecha', 'hora', 'estado')
    list_filter = ('fecha', 'estado', 'pista')
    search_fields = ('cliente__nombre', 'pista__numero')
    date_hierarchy = 'fecha'
    raw_id_fields = ('cliente', 'pista')


@admin.register(Partida)
class PartidaAdmin(admin.ModelAdmin):
    list_display = ('reserva', 'pista', 'empezada', 'finalizada', 'fecha_inicio')
    list_filter = ('empezada', 'finalizada', 'fecha_inicio')
    raw_id_fields = ('reserva',)


@admin.register(Jugador)
class JugadorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'partida', 'orden')
    list_filter = ('partida__reserva__fecha',)
    search_fields = ('nombre',)


class FrameInline(admin.TabularInline):
    model = Frame
    extra = 0
    fields = ('numero', 'tiro1', 'tiro2', 'tiro3', 'puntaje_frame', 'puntaje_acumulado')
    readonly_fields = ('puntaje_frame', 'puntaje_acumulado')


@admin.register(Frame)
class FrameAdmin(admin.ModelAdmin):
    list_display = ('jugador', 'numero', 'tiro1', 'tiro2', 'tiro3', 'puntaje_acumulado')
    list_filter = ('jugador__partida', 'numero')
    inlines = []


# ==============================================================================
# CAFETERÍA Y PEDIDOS
# ==============================================================================

@admin.register(Cafeteria)
class CafeteriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'horario_apertura', 'horario_cierre')


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'disponible')
    list_filter = ('disponible',)
    search_fields = ('nombre',)
    list_editable = ('precio', 'disponible')


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'reserva', 'cliente', 'fecha', 'precio_total', 'estado')
    list_filter = ('fecha', 'estado')
    raw_id_fields = ('reserva', 'cliente')


@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'menu', 'cantidad', 'subtotal')
    raw_id_fields = ('pedido', 'menu')


# ==============================================================================
# CONTACTO
# ==============================================================================

@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'email', 'fecha', 'leido')
    list_filter = ('leido', 'fecha')
    search_fields = ('nombre', 'email', 'mensaje')
    readonly_fields = ('nombre', 'email', 'mensaje', 'fecha')
    actions = ['marcar_como_leido']

    def marcar_como_leido(self, request, queryset):
        queryset.update(leido=True)
    marcar_como_leido.short_description = "Marcar seleccionados como leídos"