from django.db import models
from django.contrib.auth.models import User, AbstractUser

# ----- Tipo de pista de bowling -----
class TipoPista(models.Model):
    tipo = models.CharField(max_length=100, unique=True)
    zona = models.CharField(max_length=50)
    precio = models.FloatField()
    descuento = models.FloatField(default=0.0)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.tipo


# ----- Estado general de una pista o reserva -----
class Estado(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre


# ----- Representa una pista física -----
class Pista(models.Model):
    id_pista = models.AutoField(primary_key=True)
    capacidad_maxima = models.IntegerField()
    tipo_pista = models.ForeignKey(TipoPista, on_delete=models.CASCADE, null=True, blank=True)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE, null=True, blank=True)
    numero = models.PositiveIntegerField(unique=True, null=True, blank=True)

    def __str__(self):
        tipo = self.tipo_pista.tipo if self.tipo_pista else "Sin tipo"
        precio = self.tipo_pista.precio if self.tipo_pista else "?"
        return f"Pista {self.numero} - {tipo} (${precio})"


from django.conf import settings

# ----- Representa al cliente que realiza reservas -----
class Cliente(models.Model):
    id_cliente = models.AutoField(primary_key=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20)
    email = models.EmailField()

    def __str__(self):
        return self.nombre


# ----- Usuario del sistema (admin o cliente) -----
class Usuario(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Administrador'),
        ('cliente', 'Cliente'),
    )
    # Campo personalizado para definir el rol
    rol = models.CharField(max_length=20, choices=ROLE_CHOICES, default='cliente')
    REQUIRED_FIELDS = []


# ----- Registro de reservas de pistas -----
class Reserva(models.Model):
    id_reserva = models.AutoField(primary_key=True)
    fecha = models.DateField()
    hora = models.TimeField()
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True, blank=True)
    pista = models.ForeignKey(Pista, on_delete=models.CASCADE, null=True, blank=True)
    precio_total = models.FloatField(default=0.0)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE, null=True, blank=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Reserva {self.id_reserva}"


# ----- Partida de bowling asociada a una reserva -----
class Partida(models.Model):
    id_partida = models.AutoField(primary_key=True)
    pista = models.ForeignKey(Pista, on_delete=models.CASCADE, null=True, blank=True)
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, null=True, blank=True)
    duracion = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f"Partida {self.id_partida}"


# ----- Perfil extendido del usuario -----
class PerfilUsuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, null=True, blank=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True, blank=True)
    nombre_usuario = models.CharField(max_length=50)
    email = models.EmailField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    contraseña = models.CharField(max_length=100, default='1234')

    def __str__(self):
        return self.nombre_usuario


# ----- Jugador de las partidas -----
class Jugador(models.Model):
    id_jugador = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    edad = models.IntegerField(null=True, blank=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.nombre


# ----- Comidas disponibles en la cafetería -----
class comida(models.Model):
    id_comida = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.FloatField()

    def __str__(self):
        return self.nombre


# ----- Estadísticas de rendimiento del jugador -----
class EstadisticasJugador(models.Model):
    id_estadistica = models.AutoField(primary_key=True)
    jugador = models.ForeignKey(Jugador, on_delete=models.CASCADE)
    partidas_jugadas = models.IntegerField(default=0)
    promedio_puntaje = models.FloatField(default=0.0)
    total_strikes = models.IntegerField(default=0)
    total_spares = models.IntegerField(default=0)

    def __str__(self):
        return f"Estadísticas {self.jugador.nombre}"


# ----- Relación entre jugadores y partidas -----
class JugadorPartida(models.Model):
    id_jugador_partida = models.AutoField(primary_key=True)
    jugador = models.ForeignKey(Jugador, on_delete=models.CASCADE)
    partida = models.ForeignKey(Partida, on_delete=models.CASCADE)
    puntaje_final = models.IntegerField(default=0)
    posicion = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.jugador.nombre} - Partida {self.partida.id_partida}"


# ----- Turnos de cada jugador en una partida -----
class Turno(models.Model):
    id_turno = models.AutoField(primary_key=True)
    numero_turno = models.IntegerField()
    lanzamiento1 = models.IntegerField(default=0)
    lanzamiento2 = models.IntegerField(default=0)
    lanzamiento3 = models.IntegerField(default=0)
    puntaje_turno = models.IntegerField(default=0)
    bonus = models.IntegerField(default=0)
    strike = models.BooleanField(default=False)
    spare = models.BooleanField(default=False)
    partida = models.ForeignKey(Partida, on_delete=models.CASCADE, null=True, blank=True)
    jugador_partida = models.ForeignKey(JugadorPartida, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Turno {self.numero_turno} - {self.jugador_partida}"


# ----- Cafetería asociada al bowling -----
class Cafeteria(models.Model):
    id_cafeteria = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    horario_apertura = models.TimeField()
    horario_cierre = models.TimeField()
    capacidad_maxima = models.IntegerField()
    email = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.nombre


# ----- Menú disponible en la cafetería -----
class Menu(models.Model):
    id_menu = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.FloatField()

    def __str__(self):
        return self.nombre


# ----- Pedido realizado por un cliente -----
class Pedido(models.Model):
    id_pedido = models.AutoField(primary_key=True)
    horario = models.DateTimeField()
    precio_total = models.FloatField()
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, null=True, blank=True)
    cafeteria = models.ForeignKey(Cafeteria, on_delete=models.CASCADE, null=True, blank=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Pedido {self.id_pedido}"


# ----- Detalle de los ítems de cada pedido -----
class DetallePedido(models.Model):
    id_detalle_pedido = models.AutoField(primary_key=True)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    subtotal = models.FloatField()

    def __str__(self):
        return f"{self.cantidad} x {self.menu.nombre} para {self.cliente.nombre}"


# ----- Mensajes enviados desde el formulario de contacto -----
class Mensaje(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    mensaje = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} - {self.email}"
