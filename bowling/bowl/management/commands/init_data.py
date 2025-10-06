import os
import django

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth.models import User

from django.core.management.base import BaseCommand
from bowl.models import (
    TipoPista, Estado, Pista, Cliente, Usuario, Reserva, Partida,
    Jugador, EstadisticasJugador, JugadorPartida, Turno,
    comida, Cafeteria, Menu, Pedido, DetallePedido
)
from django.utils import timezone
from datetime import date, time, timedelta

# Crear el superusuario si no existe
if not User.objects.filter(username="admin").exists():
    User.objects.create_superuser("admin", "", "1234")
    print("✅ Superusuario creado: admin / 1234")
else:
    print("ℹ️ Ya existe el superusuario 'admin'")

class Command(BaseCommand):
    help = "Inicializa datos predeterminados del Centro de Bowling"

    def handle(self, *args, **kwargs):
        tipos = [
            {'tipo': 'ULTRA VIP', 'zona': 'Zona 3', 'precio': 20000, 'descuento': 10, 'descripcion': 'Total exclusividad y el mejor de los servicios.'},
            {'tipo': 'VIP', 'zona': 'Zona 2', 'precio': 15000, 'descuento': 5, 'descripcion': 'Zona semi-exclusiva y gran servicio.'},
            {'tipo': 'BASE', 'zona': 'Zona 1', 'precio': 10000, 'descuento': 0, 'descripcion': 'Zona general y con servicio base.'},
        ]
        for t in tipos:
            obj, created = TipoPista.objects.get_or_create(tipo=t['tipo'], defaults=t)
            self.stdout.write(self.style.SUCCESS(f'TipoPista "{t["tipo"]}" {"creado" if created else "ya existe"}'))

        estados = ['Disponible', 'Ocupada', 'En mantenimiento']
        for e in estados:
            obj, created = Estado.objects.get_or_create(nombre=e)
            self.stdout.write(self.style.SUCCESS(f'Estado "{e}" {"creado" if created else "ya existe"}'))

        pista1, _ = Pista.objects.get_or_create(capacidad_maxima=6, tipo_pista=TipoPista.objects.get(tipo='BASE'), estado=Estado.objects.get(nombre='Disponible'))
        pista2, _ = Pista.objects.get_or_create(capacidad_maxima=4, tipo_pista=TipoPista.objects.get(tipo='VIP'), estado=Estado.objects.get(nombre='Ocupada'))

        clientes_data = [
            {'nombre': 'Pichichi', 'direccion': 'Camino a Calera 5430', 'telefono': '54 9 351 333 5555	', 'email': 'pedonelopez@gmail.com'},
            {'nombre': 'soraya', 'direccion': 'sesese', 'telefono': '2', 'email': 'soso@gmail.com'},
        ]
        clientes = []
        for c in clientes_data:
            obj, created = Cliente.objects.get_or_create(email=c['email'], defaults=c)
            clientes.append(obj)
            self.stdout.write(self.style.SUCCESS(f'Cliente "{c["nombre"]}" {"creado" if created else "ya existe"}'))

        usuarios_data = [
            {'nombre_usuario': 'Nico_bolos', 'email': 'nicoferreyra2612@gmail.com', 'cliente': clientes[0]},
            {'nombre_usuario': 'soraya', 'email': 'soso@gmail.com', 'cliente': clientes[1]},
        ]
        for u in usuarios_data:
            obj, created = Usuario.objects.get_or_create(nombre_usuario=u['nombre_usuario'], defaults=u)
            self.stdout.write(self.style.SUCCESS(f'Usuario "{u["nombre_usuario"]}" {"creado" if created else "ya existe"}'))

        reservas_data = [
        {'fecha': date.today(), 'hora': time(18, 0), 'cliente': clientes[0], 'pista': pista1, 'precio_total': 15000, 'estado': Estado.objects.get(nombre='Disponible')},
        {'fecha': date.today() + timedelta(days=1), 'hora': time(20, 0), 'cliente': clientes[1], 'pista': pista2, 'precio_total': 8000, 'estado': Estado.objects.get(nombre='Ocupada')},
]

        reservas = []
        for r in reservas_data:
            obj, created = Reserva.objects.get_or_create(
                fecha=r['fecha'],
                hora=r['hora'],
                cliente=r['cliente'],
                pista=r['pista'],
                defaults={
                    'precio_total': r['precio_total'],
                    'estado': r['estado']
                }
            )
            reservas.append(obj)
            self.stdout.write(self.style.SUCCESS(
                f'Reserva para {r["cliente"].nombre} {"creada" if created else "ya existe"}'
            ))

        partida1, _ = Partida.objects.get_or_create(pista=pista1, reserva=reservas[0], defaults={'duracion': time(1, 0)})
        partida2, _ = Partida.objects.get_or_create(pista=pista2, reserva=reservas[1], defaults={'duracion': time(1, 30)})

        jugadores_data = [
            {'nombre': 'pichi', 'edad': 27, 'email': 'algo@gmail.com'},
            {'nombre': 'sori', 'edad': 20, 'email': 'soso@gmail.com'},
        ]
        jugadores = []
        for j in jugadores_data:
            obj, created = Jugador.objects.get_or_create(nombre=j['nombre'], defaults=j)
            jugadores.append(obj)
            self.stdout.write(self.style.SUCCESS(f'Jugador "{j["nombre"]}" {"creado" if created else "ya existe"}'))

        for j in jugadores:
            EstadisticasJugador.objects.get_or_create(jugador=j, defaults={'partidas_jugadas': 1, 'promedio_puntaje': 4.0, 'total_strikes': 1, 'total_spares': 2})

        jp1, _ = JugadorPartida.objects.get_or_create(jugador=jugadores[0], partida=partida1, defaults={'puntaje_final': 13, 'posicion': 2})
        jp2, _ = JugadorPartida.objects.get_or_create(jugador=jugadores[1], partida=partida2, defaults={'puntaje_final': 100, 'posicion': 1})

        for i in range(1, 4):
            Turno.objects.get_or_create(numero_turno=i, partida=partida1, jugador_partida=jp1, defaults={'lanzamiento1': 5, 'lanzamiento2': 4, 'puntaje_turno': 9})

        comidas_data = [
            {'nombre': 'SpaceCafé', 'descripcion': 'Café recién hecho con un toque especial.', 'precio': 3.99},
            {'nombre': 'SpaceFries', 'descripcion': 'Papas doradas y crujientes, perfectas para compartir.', 'precio': 4.99},
            {'nombre': 'SpaceNuggets', 'descripcion': 'Deliciosos nuggets crujientes con salsa a elección.', 'precio': 8.99},
            {'nombre': 'SpaceBowling Burger', 'descripcion': 'Clásica hamburguesa con carne jugosa, lechuga, queso y salsa especial.', 'precio': 12.99},
        ]
        
        for c in comidas_data:
            comida.objects.get_or_create(nombre=c['nombre'], defaults=c)

        cafe, _ = Cafeteria.objects.get_or_create(
            nombre='Bowling Café',
            defaults={'horario_apertura': time(10, 0), 'horario_cierre': time(24, 0), 'capacidad_maxima': 50, 'email': 'cafe@bowling.com', 'telefono': '3511112222'}
        )

        # === MENÚS ===
        menus_data = [
            {'nombre': 'Combo 1', 'descripcion': 'Pizza + Gaseosa', 'precio': 7000},
            {'nombre': 'Combo 2', 'descripcion': 'Hamburguesa + Gaseosa', 'precio': 6000},
        ]
        menus = []
        for m in menus_data:
            obj, _ = Menu.objects.get_or_create(nombre=m['nombre'], defaults=m)
            menus.append(obj)

        # === PEDIDOS ===
        pedido, _ = Pedido.objects.get_or_create(
            horario=timezone.now(),
            precio_total=13000,
            reserva=reservas[0],
            cafeteria=cafe,
            cliente=clientes[0]
        )

        # === DETALLES DE PEDIDO ===
        for m in menus:
            DetallePedido.objects.get_or_create(pedido=pedido, menu=m, cliente=clientes[0], defaults={'cantidad': 1, 'subtotal': m.precio})

        self.stdout.write(self.style.SUCCESS("✅ Inicialización del Centro de Bowling completada."))
    