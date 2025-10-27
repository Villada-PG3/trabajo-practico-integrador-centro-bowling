from django import forms

from .models import Pista, Cafeteria,Menu, Reserva, Mensaje, Usuario, PuntajeJugador, Jugador
from django.utils import timezone
from datetime import time
from django.contrib.auth.forms import UserCreationForm
from datetime import datetime



class RegistroUsuarioForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Se requiere un email válido")

    class Meta:
        model = Usuario
        fields = ("username", "email", "password1", "password2")



class PistaForm(forms.ModelForm):
    class Meta:
        model = Pista
        fields = ['id_pista', 'capacidad_maxima', 'tipo_pista', 'estado']

    def clean_id_pista(self):
        id_pista = self.cleaned_data['id_pista']
        if Pista.objects.filter(id_pista=id_pista).exists():
            raise forms.ValidationError("El número de pista ya existe.")
        return id_pista

class CafeteriaForm(forms.ModelForm):
    class Meta:
        model = Cafeteria
        fields = ['id_cafeteria', 'nombre', 'horario_apertura', 'horario_cierre', 'capacidad_maxima', 'email', 'telefono']

    def clean_numero(self):
        id_pista = self.cleaned_data['id_pista']
        if Pista.objects.filter(id_pista=id_pista).exists():
            raise forms.ValidationError("El número de pista ya existe.")
        return id_pista
    
class ReservaForm(forms.ModelForm):
    HORA_CHOICES = [(f"{h:02d}:00", f"{h:02d}:00") for h in range(14, 24)]

    hora = forms.ChoiceField(
        choices=HORA_CHOICES,
        label="Hora",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Reserva
        fields = ['fecha', 'hora', 'pista']

    def clean(self):
        cleaned_data = super().clean()
        pista = cleaned_data.get("pista")
        fecha = cleaned_data.get("fecha")
        hora = cleaned_data.get("hora")

        if not fecha or not hora or not pista:
            return cleaned_data

        # Convertir string "14:00" a objeto time
        if isinstance(hora, str):
            hora = datetime.strptime(hora, "%H:%M").time()
            cleaned_data["hora"] = hora

        if fecha < timezone.now().date():
            raise forms.ValidationError("No se puede reservar en fechas pasadas.")

        if Reserva.objects.filter(pista=pista, fecha=fecha, hora=hora).exists():
            raise forms.ValidationError("Esta pista ya está reservada en esa fecha y hora.")

        return cleaned_data



class CrearPistaForm(forms.ModelForm):
    class Meta:
        model = Pista
        fields = ['id_pista', 'capacidad_maxima', 'tipo_pista']

    def clean_id_pista(self):
        id_pista = self.cleaned_data['id_pista']
        if Pista.objects.filter(id_pista=id_pista).exists():
            raise forms.ValidationError("El número de pista ya existe.")
        return id_pista
    
class EditarPistaForm(forms.ModelForm):
    class Meta:
        model = Pista
        fields = ['id_pista', 'capacidad_maxima', 'tipo_pista']

    def clean_id_pista(self):
        id_pista = self.cleaned_data['id_pista']
        if Pista.objects.filter(id_pista=id_pista).exists():
            raise forms.ValidationError("El número de pista ya existe.")
        return id_pista

class ContactoForm(forms.ModelForm):
    class Meta:
        model = Mensaje
        fields = ['nombre', 'email', 'mensaje']

class MenuForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = ['nombre', 'descripcion', 'precio']
class JugadorForm(forms.ModelForm):
    class Meta:
        model = Jugador
        fields = ['nombre']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'jugador-input',
                'placeholder': 'Nombre del jugador',
                'style': 'padding: 8px; margin: 5px; width: 200px;'
            })
        }

class PuntajeForm(forms.ModelForm):
    class Meta:
        model = PuntajeJugador
        fields = ['puntaje']
        widgets = {
            'puntaje': forms.NumberInput(attrs={
                'class': 'puntaje-input',
                'min': '0',
                'max': '300',
                'style': 'width: 50px; text-align: center;'
            })
        }