# bowl/management/commands/init_data.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, time, timedelta

from bowl.models import (
    TipoPista, Estado, Pista, Cliente, Reserva, Partida,
    Jugador, Frame, Cafeteria, Menu, Pedido, DetallePedido, Usuario
)

class Command(BaseCommand):
    help = "Inicializa datos predeterminados del Centro de Bowling"

    def handle(self, *args, **kwargs):
        User = get_user_model()

        # === ADMIN ===
        if not Usuario.objects.filter(username='admin_local').exists():
            admin_user = Usuario(username='admin_local', email='adminlocal@bowling.com', rol='admin', is_staff=True, is_superuser=True)
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Usuario administrador "admin_local" creado.'))
        else:
            self.stdout.write(self.style.WARNING('Usuario administrador "admin_local" ya existe.'))

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
        estados = ['Disponible', 'Ocupada', 'En mantenimiento', 'Pendiente', "Completada", "Cancelada"]
        for e in estados:
            obj, created = Estado.objects.get_or_create(nombre=e)
            self.stdout.write(self.style.SUCCESS(f'Estado "{e}" {"creado" if created else "ya existe"}'))

        # === PISTAS ===
        Pista.objects.all().delete()
        estado_disponible = Estado.objects.get(nombre="Disponible")
        tipo_base = TipoPista.objects.get(tipo="BASE")
        tipo_vip = TipoPista.objects.get(tipo="VIP")
        tipo_ultravip = TipoPista.objects.get(tipo="ULTRA VIP")

        for i in range(1, 5):
            Pista.objects.create(numero=i, capacidad_maxima=6, tipo_pista=tipo_base, estado=estado_disponible)
        for i in range(5, 8):
            Pista.objects.create(numero=i, capacidad_maxima=6, tipo_pista=tipo_vip, estado=estado_disponible)
        for i in range(8, 11):
            Pista.objects.create(numero=i, capacidad_maxima=6, tipo_pista=tipo_ultravip, estado=estado_disponible)

        self.stdout.write(self.style.SUCCESS("Pistas creadas exitosamente."))

        # === CLIENTES Y USUARIOS ===
        clientes_data = [
            {'nombre': 'Pichichi', 'direccion': 'Camino a Calera 5430', 'telefono': '54 9 351 333 5555', 'email': 'pedonelopez@gmail.com', 'username': 'Nico_bolos'},
            {'nombre': 'soraya', 'direccion': 'sesese', 'telefono': '2', 'email': 'soso@gmail.com', 'username': 'soraya'},
        ]
        clientes = []
        for c in clientes_data:
            user, _ = Usuario.objects.get_or_create(username=c['username'], defaults={'email': c['email'], 'rol':'cliente'})
            user.set_password('1234')
            user.save()
            cliente, _ = Cliente.objects.get_or_create(email=c['email'], defaults={'nombre': c['nombre'], 'direccion': c['direccion'], 'telefono': c['telefono'], 'user': user})
            clientes.append(cliente)
            self.stdout.write(self.style.SUCCESS(f'Cliente "{cliente.nombre}" creado con usuario "{user.username}"'))

        # === RESERVAS Y PARTIDAS ===
        pista1 = Pista.objects.get(numero=1)
        pista2 = Pista.objects.get(numero=2)

        

        partidas = []
        

            # CAMBIO 2: Partida ya no tiene 'duracion' ni 'pista' obligatorio así
            
        # === JUGADORES ===
        
            # CREAMOS LOS 10 FRAMES PARA CADA JUGADOR
            
        # === CAFETERIA Y MENU ===
        cafe, _ = Cafeteria.objects.get_or_create(
            nombre='Bowling Café',
            defaults={
                'horario_apertura': time(14, 0),
                'horario_cierre': time(23, 0),
                'capacidad_maxima': 60
            }
        )

        menus_data = [
            {'nombre': 'SpaceCafé', 'descripcion': 'Café recién hecho', 'precio': 350},
            {'nombre': 'SpaceFries', 'descripcion': 'Papas doradas', 'precio': 600},
            {'nombre': 'SpaceNuggets', 'descripcion': 'Nuggets crujientes', 'precio': 1200},
            {'nombre': 'SpaceBowling Burger', 'descripcion': 'Hamburguesa', 'precio': 1800},
            {'nombre': 'SpaceGaseosa', 'descripcion': 'Gaseosa', 'precio': 400},
        ]
        menus = []
        for m in menus_data:
            menu, _ = Menu.objects.get_or_create(nombre=m['nombre'], defaults=m)
            menus.append(menu)

        # === PEDIDO DE PRUEBA ===

        self.stdout.write(self.style.SUCCESS("Inicialización completada."))