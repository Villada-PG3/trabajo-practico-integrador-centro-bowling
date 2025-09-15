from django.contrib import admin
from django.urls import path
from bowl.views import inicio, cafe
from bowl.views import inicio, ReservaView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', inicio, name="inicio"),
    path('reserva/', ReservaView.as_view(), name="reserva"),
    path('cafe/', cafe, name="cafe"),
]