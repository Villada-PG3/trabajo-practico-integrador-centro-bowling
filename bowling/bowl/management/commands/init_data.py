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
            # get_or_create evita duplicados
            obj, created = TipoPista.objects.get_or_create(tipo=t['tipo'], defaults=t)
            self.stdout.write(self.style.SUCCESS(f'TipoPista "{t["tipo"]}" {"creado" if created else "ya existe"}'))

        # === ESTADOS ===
        estados = ['Disponible', 'Ocupada', 'En mantenimiento', 'Pendiente']
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

        reservas_data = [
            {'fecha': date.today(), 'hora': time(18, 0), 'cliente': clientes[0], 'pista': pista1, 'precio_total': 15000, 'estado': Estado.objects.get(nombre='Disponible')},
            {'fecha': date.today() + timedelta(days=1), 'hora': time(20, 0), 'cliente': clientes[1], 'pista': pista2, 'precio_total': 8000, 'estado': Estado.objects.get(nombre='Ocupada')},
        ]
        reservas = []
        partidas = []
        for r in reservas_data:
            reserva, _ = Reserva.objects.get_or_create(fecha=r['fecha'], hora=r['hora'], cliente=r['cliente'], pista=r['pista'], defaults={'precio_total': r['precio_total'], 'estado': r['estado'], 'usuario': r['cliente'].user})
            reservas.append(reserva)
            partida, _ = Partida.objects.get_or_create(pista=r['pista'], reserva=reserva, cliente=r['cliente'], duracion=time(1,0))
            partidas.append(partida)
            self.stdout.write(self.style.SUCCESS(f'Reserva y Partida creadas para {r["cliente"].nombre}'))

        # === JUGADORES y Estadísticas ===
        jugadores_data = ['pichi', 'sori']
        jugadores = []
        for i, jnombre in enumerate(jugadores_data):
            jugador, _ = Jugador.objects.get_or_create(nombre=jnombre, partida=partidas[i])
            jugadores.append(jugador)
            EstadisticasJugador.objects.get_or_create(jugador=jugador, defaults={'partidas_jugadas':1,'promedio_puntaje':4.0,'total_strikes':1,'total_spares':2})
            self.stdout.write(self.style.SUCCESS(f'Jugador "{jnombre}" creado y estadística inicializada.'))

        # === JugadorPartida y Turnos ===
        for i, jugador in enumerate(jugadores):
            jp, _ = JugadorPartida.objects.get_or_create(jugador=jugador, partida=partidas[i], defaults={'puntaje_final':10*(i+1), 'posicion': i+1})
            for t in range(1,4):
                Turno.objects.get_or_create(numero_turno=t, partida=partidas[i], jugador_partida=jp, defaults={'lanzamiento1':5,'lanzamiento2':4,'puntaje_turno':9})

        # === COMIDAS, CAFETERIA, MENUS y PEDIDOS ===
        comidas_data = [
            {'nombre': 'SpaceCafé', 'descripcion': 'Café recién hecho', 'precio': 3.99},
            {'nombre': 'SpaceFries', 'descripcion': 'Papas doradas', 'precio': 4.99},
            {'nombre': 'SpaceNuggets', 'descripcion': 'Nuggets crujientes', 'precio': 8.99},
            {'nombre': 'SpaceBowling Burger', 'descripcion': 'Hamburguesa', 'precio': 12.99},
            {'nombre': 'SpaceGaseosa', 'descripcion': 'Gaseosa', 'precio': 2.99},
        ]
        for c in comidas_data:
            Comida.objects.get_or_create(nombre=c['nombre'], defaults=c)

        cafe, _ = Cafeteria.objects.get_or_create(nombre='Bowling Café', defaults={'horario_apertura':time(10,0),'horario_cierre':time(23,0),'capacidad_maxima':10,'email':'cafe@bowling.com','telefono':'3511112222'})

        menus_data = [
            {'nombre':'Espacial 1','descripcion':'Spacegaseosa + Spacenuggets','precio':10},
            {'nombre':'Espacial 2','descripcion':'SpaceBowling Burguer + gaseosa','precio':15},
            {'nombre':'Espacial 3','descripcion':'SpaceBowling Burguer + Spacefries','precio':16},
            {'nombre':'Espacial 4','descripcion':'Spacecafe','precio':2.99},
        ]
        menus = []
        for m in menus_data:
            menu, _ = Menu.objects.get_or_create(nombre=m['nombre'], defaults=m)
            menus.append(menu)

        pedido, _ = Pedido.objects.get_or_create(horario=timezone.now(), precio_total=13000, reserva=reservas[0], cafeteria=cafe, cliente=clientes[0])
        for menu in menus:
            DetallePedido.objects.get_or_create(pedido=pedido, menu=menu, cliente=clientes[0], defaults={'cantidad':1, 'subtotal':menu.precio})

        self.stdout.write(self.style.SUCCESS("✅ Inicialización completada."))
