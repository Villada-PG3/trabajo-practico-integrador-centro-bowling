# config/urls.py
from django import views
from django.contrib import admin
from django.urls import path,include
from bowl.views import (
    InicioView, CafeView, ReservaListView, ListaPistasView, CrearPistaView, EditarPistaView,
    LoginnView, ContactoView, AsignarAdminView, registro, ReservaCreateView, 
    TableroPuntuacionesView, GestionReservaView, CocinaView
)
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),

    # Inicio y básicos
    path('', InicioView.as_view(), name="inicio"),
    path('cafe/', CafeView.as_view(), name="cafe"),
    path('iniciar_sesion/', LoginnView.as_view(), name="iniciar_sesion"),

    # Reservas
    path('reserva/', ReservaListView.as_view(), name='reserva'),         # Ver todas las reservas
    path('reserva/nueva/', ReservaCreateView.as_view(), name='nueva_reserva1'),  # Crear reserva

    # Pistas
    path('pistas/', ListaPistasView.as_view(), name="lista_pistas"),
    path('pistas/crear/', CrearPistaView.as_view(), name="crear_pista"),
    path('pistas/<int:pk>/editar/', EditarPistaView.as_view(), name="editar_pista"),
    
    
    path('tablero/<int:pk>/', TableroPuntuacionesView.as_view(), name='tablero_puntuaciones'),
 
    #LogOut
    path('cerrar_sesion/', LogoutView.as_view(next_page='inicio'), name='cerrar_sesion'),
     path('registro/', registro, name='registro'),

    #Asignar Admin
    path('asignar_admin/', AsignarAdminView.as_view(), name='asignar'),

    #Contacto
    path('contacto/', ContactoView.as_view(), name='contacto'),

    path('mi_reserva/<int:pk>/', GestionReservaView.as_view(), name='gestion_reserva'),
    path('cocina/', CocinaView.as_view(), name='cocina'),
]