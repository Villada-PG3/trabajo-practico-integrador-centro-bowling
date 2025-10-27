from django.contrib import admin  # Importa el módulo admin para registrar los modelos en el panel de administración
from .models import (  # Importa todos los modelos definidos en models.py para poder usarlos en el admin
    Jugador, EstadisticasJugador, Pista, TipoPista, Usuario, Reserva, Estado,
    Partida, Turno, JugadorPartida, Cafeteria, Menu, Pedido, DetallePedido, Cliente, Comida, Mensaje, PuntajeJugador
)

<<<<<<< HEAD
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
=======
# ------------------------- MODELO JUGADOR -------------------------
@admin.register(Jugador)  # Registra el modelo Jugador en el panel admin
class JugadorAdmin(admin.ModelAdmin):  # Personaliza la vista de Jugador en el panel
    list_display = ('id_jugador', 'nombre', 'edad', 'email')  # Campos que se muestran en la lista
    search_fields = ('nombre', 'email')  # Campos por los que se puede buscar

# --------------------- MODELO ESTADISTICASJUGADOR -----------------
>>>>>>> f15d8a83d7642d7c398b0061ff5b68592723d23d
@admin.register(EstadisticasJugador)
class EstadisticasJugadorAdmin(admin.ModelAdmin):
    list_display = ('id_estadistica', 'jugador', 'partidas_jugadas', 'promedio_puntaje', 'total_strikes', 'total_spares')
    search_fields = ('jugador__nombre',)  # Permite buscar por el nombre del jugador relacionado

<<<<<<< HEAD
# === ADMIN DE PISTA ===
@admin.register(Pista)
class PistaAdmin(admin.ModelAdmin):
    list_display = ('id_pista', 'numero', 'capacidad_maxima', 'estado', 'tipo_pista')
    search_fields = ('numero',)

# === ADMIN DE ESTADO ===
=======
# ------------------------- MODELO PISTA ----------------------------
@admin.register(Pista)
class PistaAdmin(admin.ModelAdmin):
    list_display = ('id_pista', 'capacidad_maxima', 'estado', 'tipo_pista')  # Campos que se muestran
    search_fields = ('id_pista',)  # Permite buscar por ID de pista

# -------------------------- MODELO ESTADO --------------------------
>>>>>>> f15d8a83d7642d7c398b0061ff5b68592723d23d
@admin.register(Estado)
class EstadoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')  # Muestra ID y nombre del estado
    search_fields = ('nombre',)  # Permite buscar por nombre

<<<<<<< HEAD
# === ADMIN DE COMIDA ===
@admin.register(Comida)
=======
# -------------------------- MODELO COMIDA --------------------------
@admin.register(comida)
>>>>>>> f15d8a83d7642d7c398b0061ff5b68592723d23d
class ComidaAdmin(admin.ModelAdmin):
    list_display = ('id_comida', 'nombre', 'descripcion', 'precio')  # Campos visibles en la lista
    search_fields = ('nombre',)  

<<<<<<< HEAD
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
=======
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
>>>>>>> f15d8a83d7642d7c398b0061ff5b68592723d23d
@admin.register(Partida)
class PartidaAdmin(admin.ModelAdmin):
    list_display = ('id_partida', 'cliente', 'pista', 'reserva', 'duracion', 'puntaje_final')

<<<<<<< HEAD
# === ADMIN DE JUGADORPARTIDA ===
=======
# ----------------------- MODELO JUGADORPARTIDA ---------------------
>>>>>>> f15d8a83d7642d7c398b0061ff5b68592723d23d
@admin.register(JugadorPartida)
class JugadorPartidaAdmin(admin.ModelAdmin):
    list_display = ('id_jugador_partida', 'jugador', 'partida', 'puntaje_final', 'posicion') 

<<<<<<< HEAD
# === ADMIN DE TURNO ===
=======
# ---------------------------- MODELO TURNO -------------------------
# ---------------------------- MODELO TURNO -------------------------
>>>>>>> f15d8a83d7642d7c398b0061ff5b68592723d23d
@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = (  # Muestra todos los campos del turno en la lista
        'id_turno', 'numero_turno', 'partida', 'jugador_partida', 'lanzamiento1', 'lanzamiento2',
        'lanzamiento3', 'puntaje_turno', 'bonus', 'strike', 'spare',
        'falta1', 'falta2', 'falta3', 'frame_final'
    )
    list_filter = ('partida', 'jugador_partida')  # Filtros laterales por partida o jugador
    
    # Agrega estos métodos para los campos que no existen en el modelo
    def falta1(self, obj):
        return "No"  # O el valor que corresponda
    falta1.short_description = 'Falta 1'
    
    def falta2(self, obj):
        return "No"
    falta2.short_description = 'Falta 2'
    
    def falta3(self, obj):
        return "No"
    falta3.short_description = 'Falta 3'
    
    def frame_final(self, obj):
        return "0"
    frame_final.short_description = 'Frame Final'

<<<<<<< HEAD
# === ADMIN DE CAFETERÍA ===
@admin.register(Cafeteria)
class CafeteriaAdmin(admin.ModelAdmin):
    list_display = ('id_cafeteria', 'nombre', 'horario_apertura', 'horario_cierre')

    def has_add_permission(self, request):
        if Cafeteria.objects.exists():
            return False
        return True

# === ADMIN DE MENÚ ===
=======
# --------------------------- MODELO CAFETERIA ----------------------
@admin.register(Cafeteria)
class CafeteriaAdmin(admin.ModelAdmin):
    list_display = ('id_cafeteria', 'nombre', 'horario_apertura', 'horario_cierre')  # Campos visibles
    
    def has_add_permission(self, request):  # Permite solo una cafetería
        if Cafeteria.objects.exists():  
            return False 
        return True

# ----------------------------- MODELO MENU -------------------------
>>>>>>> f15d8a83d7642d7c398b0061ff5b68592723d23d
@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ('id_menu', 'nombre', 'descripcion', 'precio')  # Campos visibles
    search_fields = ('nombre',)  # Permite buscar por nombre

<<<<<<< HEAD
# === ADMIN DE PEDIDO ===
=======
# ---------------------------- MODELO PEDIDO ------------------------
>>>>>>> f15d8a83d7642d7c398b0061ff5b68592723d23d
@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id_pedido', 'horario', 'precio_total', 'reserva', 'cafeteria', 'cliente')  # Campos visibles
    list_filter = ('horario',)  # Filtro por horario

<<<<<<< HEAD
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
=======
# ------------------------- MODELO DETALLEPEDIDO --------------------
@admin.register(DetallePedido)
class DetallePedidoAdmin(admin.ModelAdmin):
    list_display = ('id_detalle_pedido', 'pedido', 'menu', 'cliente', 'cantidad', 'subtotal')  # Campos visibles
>>>>>>> f15d8a83d7642d7c398b0061ff5b68592723d23d
