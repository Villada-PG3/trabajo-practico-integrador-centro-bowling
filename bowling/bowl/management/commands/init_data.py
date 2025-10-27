# bowl/management/commands/init_data.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, time, timedelta

from bowl.models import (
    TipoPista, Estado, Pista, Cliente, Reserva, Partida,
    Jugador, EstadisticasJugador, JugadorPartida, Turno,
    Comida, Cafeteria, Menu, Pedido, DetallePedido, Usuario
)

class Command(BaseCommand):
    help = "Inicializa datos predeterminados del Centro de Bowling"

    def handle(self, *args, **kwargs):
        User = get_user_model()

        if not Usuario.objects.filter(username='admin_local').exists():
            admin_user = Usuario(username='admin_local', email='adminlocal@bowling.com', rol='admin', is_staff=True, is_superuser=True)
            admin_user.set_password('admin123')

        User = get_user_model()  # Obtiene el modelo de usuario configurado en settings.py
        admin_data = {
            'username': 'admin_local',
            'email': 'adminlocal@bowling.com',
            'rol': 'admin',
            'password': 'admin123'
        }
        if not User.objects.filter(username=admin_data['username']).exists():
            admin_user = User(
                username=admin_data['username'],
                email=admin_data['email'],
                rol=admin_data['rol'],
                is_staff=True,
                is_superuser=True
            )
            admin_user.set_password(admin_data['password'])
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f'Usuario administrador "{admin_data["username"]}" creado exitosamente.'))

        # === TIPOS DE PISTA ===
        tipos = [
            {'tipo': 'ULTRA VIP', 'zona': 'Zona 3', 'precio': 20000, 'descuento': 10, 'descripcion': 'Total exclusividad y el mejor de los servicios.'},
            {'tipo': 'VIP', 'zona': 'Zona 2', 'precio': 15000, 'descuento': 5, 'descripcion': 'Zona semi-exclusiva y gran servicio.'},
            {'tipo': 'BASE', 'zona': 'Zona 1', 'precio': 10000, 'descuento': 0, 'descripcion': 'Zona general y con servicio base.'},
        ]
        for t in tipos:
            obj, created = TipoPista.objects.get_or_create(tipo=t['tipo'], defaults=t)
            self.stdout.write(self.style.SUCCESS(f'TipoPista "{t["tipo"]}" {"creado" if created else "ya existe"}'))

        # === ESTADOS ===
        estados = ['Disponible', 'Ocupada', 'En mantenimiento', 'Pendiente']
        for e in estados:
            obj, created = Estado.objects.get_or_create(nombre=e)
            self.stdout.write(self.style.SUCCESS(f'Estado "{e}" {"creado" if created else "ya existe"}'))

        # === PISTAS - CON VERIFICACIÓN ANTES DE CREAR ===
        estado_disponible = Estado.objects.get(nombre="Disponible")
        tipo_base = TipoPista.objects.get(tipo="BASE")
        tipo_vip = TipoPista.objects.get(tipo="VIP")
        tipo_ultravip = TipoPista.objects.get(tipo="ULTRA VIP")

        # Crear pistas Base (1-4) con verificación
        for i in range(1, 5):
            if not Pista.objects.filter(numero=i).exists():
                Pista.objects.create(
                    numero=i,
                    capacidad_maxima=6,
                    tipo_pista=tipo_base,
                    estado=estado_disponible
                )
                self.stdout.write(self.style.SUCCESS(f'Pista BASE {i} creada'))
            else:
                self.stdout.write(self.style.WARNING(f'Pista {i} ya existe'))

        # Crear pistas VIP (5-7) con verificación
        for i in range(5, 8):
            if not Pista.objects.filter(numero=i).exists():
                Pista.objects.create(
                    numero=i,
                    capacidad_maxima=6,
                    tipo_pista=tipo_vip,
                    estado=estado_disponible
                )
                self.stdout.write(self.style.SUCCESS(f'Pista VIP {i} creada'))
            else:
                self.stdout.write(self.style.WARNING(f'Pista {i} ya existe'))

        # Crear pistas UltraVIP (8-10) con verificación
        for i in range(8, 11):
            if not Pista.objects.filter(numero=i).exists():
                Pista.objects.create(
                    numero=i,
                    capacidad_maxima=6,
                    tipo_pista=tipo_ultravip,
                    estado=estado_disponible
                )
                self.stdout.write(self.style.SUCCESS(f'Pista ULTRA VIP {i} creada'))
            else:
                self.stdout.write(self.style.WARNING(f'Pista {i} ya existe'))

        self.stdout.write(self.style.SUCCESS("Pistas creadas exitosamente."))

        # ... (el resto del código se mantiene igual)
        # CONTINÚA CON CLIENTES, RESERVAS, ETC...

        self.stdout.write(self.style.SUCCESS("✅ Inicialización completada exitosamente!"))