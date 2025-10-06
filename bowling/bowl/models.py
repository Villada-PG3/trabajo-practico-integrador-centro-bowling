from django.db import models
from django.contrib.auth.models import User

class TipoPista(models.Model):
    tipo = models.CharField(max_length=100, unique=True)
    zona = models.CharField(max_length=50)
    precio = models.FloatField()
    descuento = models.FloatField(default=0.0)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.tipo

class Estado(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre

class Pista(models.Model):
    id_pista = models.AutoField(primary_key=True)
    capacidad_maxima = models.IntegerField()
    tipo_pista = models.ForeignKey(TipoPista, on_delete=models.CASCADE, null=True, blank=True)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Pista {self.id_pista}"

class Cliente(models.Model):
    id_cliente = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20)
    email = models.EmailField()

    def __str__(self):
        return self.nombre

class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True, blank=True)
    nombre_usuario = models.CharField(max_length=50)
    email = models.EmailField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    contraseña = models.CharField(max_length=100, default='1234')

    def __str__(self):
        return self.nombre_usuario

class Reserva(models.Model):
    id_reserva = models.AutoField(primary_key=True)
    fecha = models.DateField()
    hora = models.TimeField()
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True, blank=True)
    pista = models.ForeignKey(Pista, on_delete=models.CASCADE, null=True, blank=True)
    precio_total = models.FloatField(default=0.0)
    estado = models.ForeignKey(Estado, on_delete=models.CASCADE, null=True, blank=True) 

    def __str__(self):
        return f"Reserva {self.id_reserva}"

class Partida(models.Model):
    id_partida = models.AutoField(primary_key=True)
    pista = models.ForeignKey(Pista, on_delete=models.CASCADE, null=True, blank=True)
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, null=True, blank=True)
    duracion = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f"Partida {self.id_partida}"

class Jugador(models.Model):
    id_jugador = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    edad = models.IntegerField(null=True, blank=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.nombre
class comida (models.Model):
    id_comida = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.FloatField()

    def __str__(self):
        return self.nombre

class EstadisticasJugador(models.Model):
    id_estadistica = models.AutoField(primary_key=True)
    jugador = models.ForeignKey(Jugador, on_delete=models.CASCADE)
    partidas_jugadas = models.IntegerField(default=0)
    promedio_puntaje = models.FloatField(default=0.0)
    total_strikes = models.IntegerField(default=0)
    total_spares = models.IntegerField(default=0)

    def __str__(self):
        return f"Estadisticas {self.jugador.nombre}"

class JugadorPartida(models.Model):
    id_jugador_partida = models.AutoField(primary_key=True)
    jugador = models.ForeignKey(Jugador, on_delete=models.CASCADE)
    partida = models.ForeignKey(Partida, on_delete=models.CASCADE)
    puntaje_final = models.IntegerField(default=0)
    posicion = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.jugador.nombre} - Partida {self.partida.id_partida}"

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
    falta1 = models.BooleanField(default=False)
    falta2 = models.BooleanField(default=False)
    falta3 = models.BooleanField(default=False)
    frame_final = models.BooleanField(default=False)
    partida = models.ForeignKey(Partida, on_delete=models.CASCADE, null=True, blank=True)
    jugador_partida = models.ForeignKey(JugadorPartida, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Turno {self.numero_turno} - {self.jugador_partida}"

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

class Menu(models.Model):
    id_menu = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.FloatField()

    def __str__(self):
        return self.nombre

class Pedido(models.Model):
    id_pedido = models.AutoField(primary_key=True)
    horario = models.DateTimeField()
    precio_total = models.FloatField()
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, null=True, blank=True)
    cafeteria = models.ForeignKey(Cafeteria, on_delete=models.CASCADE, null=True, blank=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Pedido {self.id_pedido}"

class DetallePedido(models.Model):
    id_detalle_pedido = models.AutoField(primary_key=True)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    subtotal = models.FloatField()

    def __str__(self):
        return f"{self.cantidad} x {self.menu.nombre} para {self.cliente.nombre}"