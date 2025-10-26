# bowl/management/commands/init_data.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, time, timedelta

from bowl.models import (
    TipoPista, Estado, Pista, Cliente, Reserva, Partida,
    Jugador, EstadisticasJugador, JugadorPartida, Turno,
    comida, Cafeteria, Menu, Pedido, DetallePedido, Usuario
)


class Command(BaseCommand):
    help = "Inicializa datos predeterminados del Centro de Bowling"

    def handle(self, *args, **kwargs):
        User = get_user_model()  # Obtiene el modelo de usuario configurado en settings.py
        admin_data = {
            'username': 'admin_local',
            'email': 'adminlocal@bowling.com',
            'rol': 'admin',
            'password': 'admin123'
        }

        # === USUARIO ADMIN ===
        # Verifica si ya existe, sino lo crea con permisos de superusuario
        if not Usuario.objects.filter(username=admin_data['username']).exists():
            admin_user = Usuario.objects.create(
                username=admin_data['username'],
                email=admin_data['email'],
                rol=admin_data['rol'],
                password=admin_data['password']
            )
            admin_user.set_password(admin_data['password'])  # Encripta la contraseña
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f'Usuario administrador "{admin_data["username"]}" creado exitosamente.'))
        else:
            self.stdout.write(self.style.WARNING(f'Usuario administrador "{admin_data["username"]}" ya existe.'))

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
        Pista.objects.all().delete()  # Limpiar pistas existentes para no duplicar
        self.stdout.write(self.style.WARNING("Se eliminaron todas las pistas existentes."))

        estado_disponible = Estado.objects.get(nombre="Disponible")

        # Crear pistas Base
        tipo_base = TipoPista.objects.get(tipo="BASE")
        for i in range(1, 5):
            Pista.objects.create(
                numero=i,
                capacidad_maxima=6,
                tipo_pista=tipo_base,
                estado=estado_disponible
            )

        # Crear pistas VIP
        tipo_vip = TipoPista.objects.get(tipo="VIP")
        for i in range(5, 8):
            Pista.objects.create(
                numero=i,
                capacidad_maxima=6,
                tipo_pista=tipo_vip,
                estado=estado_disponible
            )

        # Crear pistas UltraVIP
        tipo_ultravip = TipoPista.objects.get(tipo="ULTRA VIP")
        for i in range(8, 11):
            Pista.objects.create(
                numero=i,
                capacidad_maxima=6,
                tipo_pista=tipo_ultravip,
                estado=estado_disponible
            )

        self.stdout.write(self.style.SUCCESS("Pistas creadas exitosamente."))

        pista1 = Pista.objects.get(numero=1)
        pista2 = Pista.objects.get(numero=2)

        # === CLIENTES ===
        clientes_data = [
            {'nombre': 'Pichichi', 'direccion': 'Camino a Calera 5430', 'telefono': '54 9 351 333 5555', 'email': 'pedonelopez@gmail.com'},
            {'nombre': 'soraya', 'direccion': 'sesese', 'telefono': '2', 'email': 'soso@gmail.com'},
        ]
        clientes = []
        for c in clientes_data:
            # Evita duplicar clientes existentes
            obj, created = Cliente.objects.get_or_create(email=c['email'], defaults=c)
            clientes.append(obj)
            self.stdout.write(self.style.SUCCESS(f'Cliente "{c["nombre"]}" {"creado" if created else "ya existe"}'))

       # === USUARIOS Y CLIENTES ===
        usuarios_data = [
            {'username': 'Nico_bolos', 'email': 'nicoferreyra2612@gmail.com', 'cliente_index': 0},
            {'username': 'soraya', 'email': 'soso@gmail.com', 'cliente_index': 1},
        ]
        for u in usuarios_data:
            user, created_user = User.objects.get_or_create(username=u['username'], defaults={'email': u['email']})
            if created_user:
                user.set_password('1234')
                user.save()
            idx = u.get('cliente_index')
            if idx is not None and idx < len(clientes):
                cliente_obj = clientes[idx]
                # Evita asignar usuario si ya está vinculado a otro cliente
                if Cliente.objects.filter(user=user).exists():
                    self.stdout.write(self.style.WARNING(
                        f'El usuario "{u["username"]}" ya está asociado a otro cliente. Saltando asignación.'
                    ))
                    continue
                # Evita sobrescribir un cliente que ya tiene usuario
                if hasattr(cliente_obj, 'user') and cliente_obj.user is not None:
                    self.stdout.write(self.style.WARNING(
                        f'El cliente "{cliente_obj.nombre}" ya tiene un usuario asignado. Saltando asignación.'
                    ))
                    continue
                # Asignar usuario al cliente
                cliente_obj.user = user
                try:
                    cliente_obj.save()
                    self.stdout.write(self.style.SUCCESS(
                        f'Usuario "{u["username"]}" asignado al cliente "{cliente_obj.nombre}"'
                    ))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(
                        f'Error al asignar usuario "{u["username"]}" al cliente "{cliente_obj.nombre}": {str(e)}'
                    ))
            self.stdout.write(self.style.SUCCESS(
                f'Usuario "{u["username"]}" {"creado" if created_user else "ya existe"}'
            ))

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
            self.stdout.write(self.style.SUCCESS(f'Reserva para {r["cliente"].nombre} {"creada" if created else "ya existe"}'))

        # Crear partidas asociadas a reservas
        partida1, _ = Partida.objects.get_or_create(pista=pista1, reserva=reservas[0], defaults={'duracion': time(1, 0)})
        partida2, _ = Partida.objects.get_or_create(pista=pista2, reserva=reservas[1], defaults={'duracion': time(1, 30)})

        # === JUGADORES Y ESTADÍSTICAS ===
        jugadores_data = [
            {'nombre': 'pichi', 'edad': 27, 'email': 'algo@gmail.com'},
            {'nombre': 'sori', 'edad': 20, 'email': 'soso@gmail.com'},
        ]
        jugadores = []
        for j in jugadores_data:
            obj, created = Jugador.objects.get_or_create(nombre=j['nombre'], defaults=j)
            jugadores.append(obj)
            self.stdout.write(self.style.SUCCESS(f'Jugador "{j["nombre"]}" {"creado" if created else "ya existe"}'))

        # Crear estadísticas iniciales de cada jugador
        for j in jugadores:
            EstadisticasJugador.objects.get_or_create(jugador=j, defaults={'partidas_jugadas': 1, 'promedio_puntaje': 4.0, 'total_strikes': 1, 'total_spares': 2})

        # Asociar jugadores a partidas
        jp1, _ = JugadorPartida.objects.get_or_create(jugador=jugadores[0], partida=partida1, defaults={'puntaje_final': 13, 'posicion': 2})
        jp2, _ = JugadorPartida.objects.get_or_create(jugador=jugadores[1], partida=partida2, defaults={'puntaje_final': 100, 'posicion': 1})

        # Crear turnos de la partida 1
        for i in range(1, 4):
            Turno.objects.get_or_create(numero_turno=i, partida=partida1, jugador_partida=jp1, defaults={'lanzamiento1': 5, 'lanzamiento2': 4, 'puntaje_turno': 9})

        # === COMIDAS ===
        comidas_data = [
            {'nombre': 'SpaceCafé', 'descripcion': 'Café recién hecho con un toque especial.', 'precio': 3.99},
            {'nombre': 'SpaceFries', 'descripcion': 'Papas doradas y crujientes, perfectas para compartir.', 'precio': 4.99},
            {'nombre': 'SpaceNuggets', 'descripcion': 'Deliciosos nuggets crujientes con salsa a elección.', 'precio': 8.99},
            {'nombre': 'SpaceBowling Burger', 'descripcion': 'Clásica hamburguesa con carne jugosa, lechuga, queso y salsa especial.', 'precio': 12.99},
            {'nombre': 'SpaceGaseosa', 'descripcion': 'Rica y refrescante gaseosa para acompañar tu comida.', 'precio': 2.99}
        ]
        for c in comidas_data:
            comida.objects.get_or_create(nombre=c['nombre'], defaults=c)  # Evita duplicar comidas

        # === CAFETERÍA Y MENÚS ===
        cafe, _ = Cafeteria.objects.get_or_create(
            nombre='Bowling Café',
            defaults={'horario_apertura': time(10, 0), 'horario_cierre': time(23, 0), 'capacidad_maxima': 10, 'email': 'cafe@bowling.com', 'telefono': '3511112222'}
        )

        menus_data = [
            {'nombre': 'Espacial 1', 'descripcion': 'Spacegaseosa + Spacenuggets', 'precio': 10},
            {'nombre': 'Espacial 2', 'descripcion': 'SpaceBowling Burguer + gaseosa', 'precio': 15},
            {'nombre': 'Espacial 3', 'descripcion': 'SpaceBowling Burguer + Spacefries', 'precio': 16},
            {'nombre': 'Espacial 4', 'descripcion': 'Spacecafe', 'precio': 2.99},
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

        for m in menus:
            DetallePedido.objects.get_or_create(pedido=pedido, menu=m, cliente=clientes[0], defaults={'cantidad': 1, 'subtotal': m.precio})

        self.stdout.write(self.style.SUCCESS("✅ Inicialización del Centro de Bowling completada."))
