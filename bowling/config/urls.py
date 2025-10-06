# config/urls.py
from django.contrib import admin
from django.urls import path,include
from bowl.views import (
    InicioView, CafeView, ReservaView, ListaPistasView, CrearPistaView, EditarPistaView, ListaComidaView, CrearCafeteriaView, EditarCafeteriaView,LoginnView
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
    path('reserva/', ReservaView.as_view(), name="reserva"),

    # Pistas
    path('pistas/', ListaPistasView.as_view(), name="lista_pistas"),
    path('pistas/crear/', CrearPistaView.as_view(), name="crear_pista"),
    path('pistas/<int:pk>/editar/', EditarPistaView.as_view(), name="editar_pista"),
    
    #Cafeteria
    path('cafeteria/', ListaComidaView.as_view(), name="lista_comida"),
    path('cafeteria/crear/', CrearCafeteriaView.as_view(), name="crear_comida"),
    path('cafeteria/<int:pk>/editar/', EditarCafeteriaView.as_view(), name="editar_comida"),

    #LogOut
    path('cerrar_sesion/', LogoutView.as_view(next_page='inicio'), name='cerrar_sesion'),
]