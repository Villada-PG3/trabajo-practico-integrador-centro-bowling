"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
<<<<<<< HEAD


from bowl.views import inicio, cafe

from bowl.views import inicio, ReservaView

=======
from bowl.views import inicio, reserva, home, pistas, eventos, cafeteria, contacto
from bowl import views
>>>>>>> b880126141b95126722b1fe4a814d37423bb8e0e

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', inicio, name="inicio"),
<<<<<<< HEAD
    path('reserva/', ReservaView.as_view(), name="reserva"),
    path('cafe/', cafe, name="cafe"),



=======
    path('reserva/', views.reserva, name="reserva"),
    path('home/', views.home, name="home"),
    path('pistas/', views.pistas, name='pistas'),
    path('eventos/', views.eventos, name='eventos'),
    path('cafeteria/', views.cafeteria, name='cafeteria'),  
    path('contacto/', views.contacto, name='contacto'),
    
>>>>>>> b880126141b95126722b1fe4a814d37423bb8e0e
]
