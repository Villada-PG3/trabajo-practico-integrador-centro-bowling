# config/urls.py
from django.contrib import admin
from django.urls import path
from bowl.views import (
    InicioView, CafeView, IniciarSesionView,
    ReservaView, ListaPistasView, CrearPistaView, EditarPistaView
)
urlpatterns = [
    path('admin/', admin.site.urls),

    # Inicio y básicos
    path('', InicioView.as_view(), name="inicio"),
    path('cafe/', CafeView.as_view(), name="cafe"),
    path('iniciar_sesion/', IniciarSesionView.as_view(), name="iniciar_sesion"),

    # Reservas
    path('reserva/', ReservaView.as_view(), name="reserva"),

    # Pistas
    path('pistas/', ListaPistasView.as_view(), name="lista_pistas"),
    path('pistas/crear/', CrearPistaView.as_view(), name="crear_pista"),
    path('pistas/<int:pk>/editar/', EditarPistaView.as_view(), name="editar_pista"),
]