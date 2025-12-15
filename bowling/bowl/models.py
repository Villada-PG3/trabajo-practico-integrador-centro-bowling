# bowl/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone


# ==============================================================================
# 1. USUARIOS Y PERFILES
# ==============================================================================

class Usuario(AbstractUser):
    """Usuario personalizado con rol"""
    ROLE_CHOICES = (
        ('admin', 'Administrador'),
        ('cliente', 'Cliente'),
    )
    rol = models.CharField(max_length=20, choices=ROLE_CHOICES, default='cliente', blank=True, null=True)

    def __str__(self):
        return self.username


class Cliente(models.Model):
    """Perfil del cliente (relación 1 a 1 con Usuario)"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True
        , default=None
    )
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} ({self.user.username})"


# ==============================================================================
# 2. ESTADOS, TIPOS Y PISTAS
# ==============================================================================

class Estado(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "Estados"


class TipoPista(models.Model):
    tipo = models.CharField(max_length=100, unique=True)
    zona = models.CharField(max_length=50, blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    descuento = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.tipo} - ${self.precio}"


class Pista(models.Model):
    id_pista = models.AutoField(primary_key=True)
    numero = models.PositiveIntegerField(unique=True, null=True, blank=True)
    capacidad_maxima = models.PositiveIntegerField(default=6, blank=True, null=True)
    tipo_pista = models.ForeignKey(TipoPista, on_delete=models.SET_NULL, null=True, blank=True)
    estado = models.ForeignKey(Estado, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        tipo = self.tipo_pista.tipo if self.tipo_pista else "Sin tipo"
        return f"Pista {self.numero} - {tipo}"

    class Meta:
        verbose_name_plural = "Pistas"
        ordering = ['numero']


# ==============================================================================
# 3. RESERVAS
# ==============================================================================

class Reserva(models.Model):
    id_reserva = models.AutoField(primary_key=True)
    fecha = models.DateField()
    hora = models.TimeField()
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True, blank=True)
    pista = models.ForeignKey(Pista, on_delete=models.SET_NULL, null=True, blank=True)
    precio_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True, null=True)
    estado = models.ForeignKey(Estado, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        hora_str = self.hora.strftime('%H:%M') if self.hora else "??:??"
        return f"Reserva {self.id_reserva} - {self.fecha} {hora_str}"

    class Meta:
        unique_together = ('pista', 'fecha', 'hora')
        ordering = ['-fecha', '-hora']


# ==============================================================================
# 4. PARTIDA DE BOWLING
# ==============================================================================

class Partida(models.Model):
    id_partida = models.AutoField(primary_key=True)
    reserva = models.OneToOneField(Reserva, on_delete=models.CASCADE, null=True, blank=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True)
    pista = models.ForeignKey(Pista, on_delete=models.SET_NULL, null=True, blank=True)
    empezada = models.BooleanField(default=False)
    finalizada = models.BooleanField(default=False)
    fecha_inicio = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        pista_num = self.pista.numero if self.pista else "?"
        fecha = self.reserva.fecha if self.reserva else "?"
        return f"Partida Pista {pista_num} - {fecha}"

    class Meta:
        verbose_name_plural = "Partidas"


class Jugador(models.Model):
    id_jugador = models.AutoField(primary_key=True)
    partida = models.ForeignKey(Partida, on_delete=models.CASCADE, related_name='jugadores', null=True, blank=True)
    nombre = models.CharField(max_length=100, blank=True, null=True)
    orden = models.PositiveIntegerField(default=0, blank=True, null=True)

    class Meta:
        ordering = ['orden']
        unique_together = ('partida', 'nombre')

    def __str__(self):
        return self.nombre or "Jugador sin nombre"

    def puntaje_total(self):
        ultimo_frame = self.frames.order_by('numero').last()
        return ultimo_frame.puntaje_acumulado if ultimo_frame else 0


class Frame(models.Model):
    jugador = models.ForeignKey(Jugador, on_delete=models.CASCADE, related_name='frames', null=True, blank=True)
    numero = models.PositiveSmallIntegerField(blank=True, null=True)  # 1 a 10

    tiro1 = models.PositiveSmallIntegerField(null=True, blank=True)
    tiro2 = models.PositiveSmallIntegerField(null=True, blank=True)
    tiro3 = models.PositiveSmallIntegerField(null=True, blank=True)

    puntaje_frame = models.PositiveSmallIntegerField(default=0, blank=True, null=True)
    puntaje_acumulado = models.PositiveIntegerField(default=0, blank=True, null=True)

    class Meta:
        unique_together = ('jugador', 'numero')
        ordering = ['numero']

    def __str__(self):
        return f"Frame {self.numero or '?'} - {self.jugador.nombre if self.jugador else 'Sin jugador'}"

    def es_strike(self):
        return self.tiro1 == 10

    def es_spare(self):
        return (self.tiro1 is not None and self.tiro2 is not None and
                self.tiro1 + self.tiro2 == 10 and self.tiro1 != 10)


# ==============================================================================
# 5. CAFETERÍA Y PEDIDOS
# ==============================================================================

class Cafeteria(models.Model):
    nombre = models.CharField(max_length=100, default="Cafetería Space Bowling", blank=True, null=True)
    horario_apertura = models.TimeField(default="14:00", blank=True, null=True)
    horario_cierre = models.TimeField(default="23:00", blank=True, null=True)
    capacidad_maxima = models.PositiveIntegerField(default=50, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.nombre or "Cafetería"


class Menu(models.Model):
    nombre = models.CharField(max_length=100, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, blank=True, null=True)
    disponible = models.BooleanField(default=True)
    imagen = models.ImageField(upload_to='menu/', blank=True, null=True)

    def __str__(self):
        return f"{self.nombre or 'Sin nombre'} - ${self.precio or 0}"


class Pedido(models.Model):
    reserva = models.ForeignKey(Reserva, on_delete=models.SET_NULL, null=True, blank=True, related_name='pedidos')
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True)
    fecha = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    estado = models.ForeignKey(Estado, on_delete=models.SET_NULL, null=True, blank=True)
    precio_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True, null=True)

    def __str__(self):
        return f"Pedido {self.id} - {self.cliente or 'Anónimo'}"


class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles', null=True, blank=True)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, null=True, blank=True)
    cantidad = models.PositiveIntegerField(default=1, blank=True, null=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.menu and self.menu.precio is not None:
            self.subtotal = (self.menu.precio or 0) * (self.cantidad or 1)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cantidad or 0}x {self.menu.nombre if self.menu else 'Item'}"


# ==============================================================================
# 6. CONTACTO Y MENSAJES
# ==============================================================================

class Mensaje(models.Model):
    nombre = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    mensaje = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    leido = models.BooleanField(default=False)

    def __str__(self):
        return f"Mensaje de {self.nombre or 'Anónimo'} - {self.fecha.strftime('%d/%m/%Y') if self.fecha else 'Sin fecha'}"

    class Meta:
        ordering = ['-fecha']
class PuntajeJugador(models.Model):
    id_puntaje = models.AutoField(primary_key=True)
    partida = models.ForeignKey(Partida, on_delete=models.CASCADE)
    jugador = models.ForeignKey(Jugador, on_delete=models.CASCADE)
    set = models.PositiveSmallIntegerField()        
    puntaje = models.PositiveSmallIntegerField(default=0)


    class Meta:
        unique_together = ('partida', 'jugador', 'set')
        verbose_name = "Puntaje por set"
        verbose_name_plural = "Puntajes por set"

    def __str__(self):
        return f"{self.jugador} - Set {self.set}: {self.puntaje}"