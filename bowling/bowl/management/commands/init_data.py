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


from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Inicializa datos predeterminados del Centro de Bowling"

    def handle(self, *args, **kwargs):

        User = get_user_model()  # Esto ahora apunta a 'bowl.Usuario'

        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin",
                password="admin123",
                email="admin@example.com"
            )
                
            


        # === TIPOS DE PISTA ===
        tipos = [
            {'tipo': 'Profesional', 'zona': 'Zona A', 'precio': 15000, 'descuento': 10, 'descripcion': 'Pista de nivel profesional con sensores avanzados.'},
            {'tipo': 'Familiar', 'zona': 'Zona B', 'precio': 8000, 'descuento': 5, 'descripcion': 'Ideal para grupos familiares.'},
            {'tipo': 'Infantil', 'zona': 'Zona C', 'precio': 6000, 'descuento': 0, 'descripcion': 'Pista adaptada para niños.'},
        ]
        for t in tipos:
            obj, created = TipoPista.objects.get_or_create(tipo=t['tipo'], defaults=t)
            self.stdout.write(self.style.SUCCESS(f'TipoPista "{t["tipo"]}" {"creado" if created else "ya existe"}'))

        # === ESTADOS DE PISTA ===
        estados = ['Disponible', 'Ocupada', 'En mantenimiento']
        for e in estados:
            obj, created = Estado.objects.get_or_create(nombre=e)
            self.stdout.write(self.style.SUCCESS(f'Estado "{e}" {"creado" if created else "ya existe"}'))

        # === PISTAS ===
        pista1, _ = Pista.objects.get_or_create(capacidad_maxima=6, tipo_pista=TipoPista.objects.get(tipo='Profesional'), estado=Estado.objects.get(nombre='Disponible'))
        pista2, _ = Pista.objects.get_or_create(capacidad_maxima=4, tipo_pista=TipoPista.objects.get(tipo='Familiar'), estado=Estado.objects.get(nombre='Ocupada'))

        # === CLIENTES ===
        clientes_data = [
            {'nombre': 'Juan Pérez', 'direccion': 'Calle 123', 'telefono': '3512345678', 'email': 'juan@example.com'},
            {'nombre': 'María López', 'direccion': 'Av. Siempreviva 742', 'telefono': '3544556677', 'email': 'maria@example.com'},
        ]
        clientes = []
        for c in clientes_data:
            obj, created = Cliente.objects.get_or_create(email=c['email'], defaults=c)
            clientes.append(obj)
            self.stdout.write(self.style.SUCCESS(f'Cliente "{c["nombre"]}" {"creado" if created else "ya existe"}'))

        # === USUARIOS ===
      #  usuarios_data = [
      #      {'nombre_usuario': 'juanp', 'email': 'juan@example.com', 'cliente': clientes[0], 'contraseña':'1234'},
     #       {'nombre_usuario': 'marial', 'email': 'maria@example.com', 'cliente': clientes[1],'contraseña':'1234'},
    #    ]
    #    for u in usuarios_data:
  #          obj, created = Usuario.objects.get_or_create(nombre_usuario=u['nombre_usuario'], defaults=u)
 #           self.stdout.write(self.style.SUCCESS(f'Usuario "{u["nombre_usuario"]}" {"creado" if created else "ya existe"}'))


        
        # === RESERVAS ===
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
        # === PARTIDAS ===
        partida1, _ = Partida.objects.get_or_create(pista=pista1, reserva=reservas[0], defaults={'duracion': time(1, 0)})
        partida2, _ = Partida.objects.get_or_create(pista=pista2, reserva=reservas[1], defaults={'duracion': time(1, 30)})

        # === JUGADORES ===
        jugadores_data = [
            {'nombre': 'Carlos Gómez', 'edad': 25, 'email': 'carlos@example.com'},
            {'nombre': 'Lucía Díaz', 'edad': 20, 'email': 'lucia@example.com'},
        ]
        jugadores = []
        for j in jugadores_data:
            obj, created = Jugador.objects.get_or_create(nombre=j['nombre'], defaults=j)
            jugadores.append(obj)
            self.stdout.write(self.style.SUCCESS(f'Jugador "{j["nombre"]}" {"creado" if created else "ya existe"}'))

        # === ESTADÍSTICAS DE JUGADORES ===
        for j in jugadores:
            EstadisticasJugador.objects.get_or_create(jugador=j, defaults={'partidas_jugadas': 10, 'promedio_puntaje': 150.0, 'total_strikes': 20, 'total_spares': 15})

        # === JUGADORES EN PARTIDAS ===
        jp1, _ = JugadorPartida.objects.get_or_create(jugador=jugadores[0], partida=partida1, defaults={'puntaje_final': 180, 'posicion': 1})
        jp2, _ = JugadorPartida.objects.get_or_create(jugador=jugadores[1], partida=partida2, defaults={'puntaje_final': 160, 'posicion': 2})

        # === TURNOS ===
        for i in range(1, 4):
            Turno.objects.get_or_create(numero_turno=i, partida=partida1, jugador_partida=jp1, defaults={'lanzamiento1': 5, 'lanzamiento2': 4, 'puntaje_turno': 9})
            Turno.objects.get_or_create(numero_turno=i, partida=partida2, jugador_partida=jp2, defaults={'lanzamiento1': 7, 'lanzamiento2': 2, 'puntaje_turno': 9})

        # === COMIDA ===
        comidas_data = [
            {'nombre': 'Pizza', 'descripcion': 'Pizza muzzarella grande', 'precio': 6000},
            {'nombre': 'Hamburguesa', 'descripcion': 'Hamburguesa completa con papas', 'precio': 5000},
        ]
        for c in comidas_data:
            comida.objects.get_or_create(nombre=c['nombre'], defaults=c)

        # === CAFETERÍAS ===
        cafe, _ = Cafeteria.objects.get_or_create(
            nombre='Bowling Café',
            defaults={'horario_apertura': time(10, 0), 'horario_cierre': time(22, 0), 'capacidad_maxima': 50, 'email': 'cafe@bowling.com', 'telefono': '3511112222'}
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
    