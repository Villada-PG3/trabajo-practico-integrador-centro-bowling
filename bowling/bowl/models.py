from django.db import models

class Pista(models.Model):
    id_pista = models.AutoField(primary_key=True)
    capacidad_maxima = models.IntegerField()

    def __str__(self):
        return f"Pista {self.id_pista}"


class Cliente(models.Model):
    id_cliente = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    telefono = models.IntegerField()
    email = models.EmailField()

    def __str__(self):
        return self.nombre


class Reserva(models.Model):
    id_reserva = models.AutoField(primary_key=True)
    fecha = models.DateField()
    hora = models.TimeField()
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    pista = models.ForeignKey(Pista, on_delete=models.CASCADE)
    estado = models.CharField(max_length=50)

    def __str__(self):
        return f"Reserva {self.id_reserva}"


class Partida(models.Model):
    id_partida = models.AutoField(primary_key=True)
    pista = models.ForeignKey(Pista, on_delete=models.CASCADE)
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE)

    def __str__(self):
        return f"Partida {self.id_partida}"


class Jugador(models.Model):
    id_jugador = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre


class Turno(models.Model):
    id_turno = models.AutoField(primary_key=True)
    numero_turno = models.IntegerField()
    lanzamiento1 = models.IntegerField()
    lanzamiento2 = models.IntegerField()
    lanzamiento3 = models.IntegerField()
    partida = models.ForeignKey(Partida, on_delete=models.CASCADE)
    jugador = models.ForeignKey(Jugador, on_delete=models.CASCADE)

    def __str__(self):
        return f"Turno {self.numero_turno} - Jugador {self.jugador}"


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
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)

    def __str__(self):
        return f"Pedido {self.id_pedido}"