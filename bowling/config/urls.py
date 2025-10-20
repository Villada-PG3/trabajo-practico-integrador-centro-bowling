# config/urls.py
from django import views
from django.contrib import admin
from django.urls import path,include
from bowl.views import (
    InicioView, CafeView, ReservaView, ListaPistasView, CrearPistaView, EditarPistaView, ListaComidaView, 
    CrearCafeteriaView, EditarCafeteriaView,LoginnView,ContactoView, AsignarAdminView, CrearComidaView, 
    registro, nosotros, GaleriaView
)
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),

    # Inicio y básicos
    path('', InicioView.as_view(), name="inicio"),
    path('cafe/', CafeView.as_view(), name="cafe"),
    path('iniciar_sesion/', LoginnView.as_view(), name="iniciar_sesion"),
    path('nosotros/', nosotros, name='nosotros'),
    path('galeria/', GaleriaView.as_view(), name='galeria'),

    # Reservas
    path('reserva/', ReservaView.as_view(), name="reserva"),

    # Pistas
    path('pistas/', ListaPistasView.as_view(), name="lista_pistas"),
    path('pistas/crear/', CrearPistaView.as_view(), name="crear_pista"),
    path('pistas/<int:pk>/editar/', EditarPistaView.as_view(), name="editar_pista"),
    
    #Cafeteria
    path('comidas/', ListaComidaView.as_view(), name='lista_comida'),
    path('comidas/crear/', CrearComidaView.as_view(), name='crear_comida'),
    path('comidas/editar/<int:pk>/', EditarCafeteriaView.as_view(), name='editar_comida'),
  
    path('cafeteria/<int:pk>/editar/', EditarCafeteriaView.as_view(), name="editar_comida"),

    #LogOut
    path('cerrar_sesion/', LogoutView.as_view(next_page='inicio'), name='cerrar_sesion'),
     path('registro/', registro, name='registro'),
    #Asignar Admin
    path('asignar_admin/', AsignarAdminView.as_view(), name='asignar'),

    #Contacto
    path('contacto/', ContactoView.as_view(), name='contacto'),
]