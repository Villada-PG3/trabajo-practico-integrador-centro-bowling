from django.contrib import admin  # Importa el módulo admin para registrar los modelos en el panel de administración
from .models import (  # Importa todos los modelos definidos en models.py para poder usarlos en el admin
    Jugador, EstadisticasJugador, Pista, TipoPista, Usuario, Reserva, Estado,
    Partida, Turno, JugadorPartida, Cafeteria, Menu, Pedido, DetallePedido, Cliente, comida
)

# ------------------------- MODELO JUGADOR -------------------------
@admin.register(Jugador)  # Registra el modelo Jugador en el panel admin
class JugadorAdmin(admin.ModelAdmin):  # Personaliza la vista de Jugador en el panel
    list_display = ('id_jugador', 'nombre', 'edad', 'email')  # Campos que se muestran en la lista
    search_fields = ('nombre', 'email')  # Campos por los que se puede buscar

# --------------------- MODELO ESTADISTICASJUGADOR -----------------
@admin.register(EstadisticasJugador)
class EstadisticasJugadorAdmin(admin.ModelAdmin):
    list_display = ('id_estadistica', 'jugador', 'partidas_jugadas', 'promedio_puntaje', 'total_strikes', 'total_spares')
    search_fields = ('jugador__nombre',)  # Permite buscar por el nombre del jugador relacionado

# ------------------------- MODELO PISTA ----------------------------
@admin.register(Pista)
class PistaAdmin(admin.ModelAdmin):
    list_display = ('id_pista', 'capacidad_maxima', 'estado', 'tipo_pista')  # Campos que se muestran
    search_fields = ('id_pista',)  # Permite buscar por ID de pista

# -------------------------- MODELO ESTADO --------------------------
@admin.register(Estado)
class EstadoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')  # Muestra ID y nombre del estado
    search_fields = ('nombre',)  # Permite buscar por nombre

# -------------------------- MODELO COMIDA --------------------------
@admin.register(comida)
class ComidaAdmin(admin.ModelAdmin):
    list_display = ('id_comida', 'nombre', 'descripcion', 'precio')  # Campos visibles en la lista
    search_fields = ('nombre',)  

# ------------------------ MODELO TIPOPISTA -------------------------
@admin.register(TipoPista)
class TipoPistaAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo', 'zona', 'precio', 'descuento', 'descripcion')  

    # Evita que se creen más de 3 tipos de pista
    def has_add_permission(self, request): 
        if TipoPista.objects.count() >= 3:  
            return False  
        return True  

# -------------------------- MODELO CLIENTE -------------------------
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('id_cliente', 'nombre', 'direccion', 'telefono', 'email') 
    search_fields = ('nombre', 'email') 

# -------------------------- MODELO RESERVA -------------------------
@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('id_reserva', 'fecha', 'hora', 'cliente', 'pista', 'precio_total', 'estado', 'usuario') 
    list_filter = ('fecha', 'estado','cliente' )  # Filtros laterales
    search_fields = ('id_reserva', 'cliente__nombre', 'pista__numero') 

# -------------------------- MODELO PARTIDA -------------------------
@admin.register(Partida)
class PartidaAdmin(admin.ModelAdmin):
    list_display = ('id_partida', 'pista', 'reserva', 'duracion')

# ----------------------- MODELO JUGADORPARTIDA ---------------------
@admin.register(JugadorPartida)
class JugadorPartidaAdmin(admin.ModelAdmin):
    list_display = ('id_jugador_partida', 'jugador', 'partida', 'puntaje_final', 'posicion') 

# ---------------------------- MODELO TURNO -------------------------
@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = (  # Muestra todos los campos del turno en la lista
        'id_turno', 'numero_turno', 'partida', 'jugador_partida', 'lanzamiento1', 'lanzamiento2',
        'lanzamiento3', 'puntaje_turno', 'bonus', 'strike', 'spare',
        'falta1', 'falta2', 'falta3', 'frame_final'
    )
    list_filter = ('partida', 'jugador_partida')  # Filtros laterales por partida o jugador

# --------------------------- MODELO CAFETERIA ----------------------
@admin.register(Cafeteria)
class CafeteriaAdmin(admin.ModelAdmin):
    list_display = ('id_cafeteria', 'nombre', 'horario_apertura', 'horario_cierre')  # Campos visibles
    
    def has_add_permission(self, request):  # Permite solo una cafetería
        if Cafeteria.objects.exists():  
            return False 
        return True

# ----------------------------- MODELO MENU -------------------------
@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('id_menu', 'nombre', 'descripcion', 'precio')  # Campos visibles
    search_fields = ('nombre',)  # Permite buscar por nombre

# ---------------------------- MODELO PEDIDO ------------------------
@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id_pedido', 'horario', 'precio_total', 'reserva', 'cafeteria', 'cliente')  # Campos visibles
    list_filter = ('horario',)  # Filtro por horario

# ------------------------- MODELO DETALLEPEDIDO --------------------
@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ('id_detalle_pedido', 'pedido', 'menu', 'cliente', 'cantidad', 'subtotal')  # Campos visibles
