from django import forms
from .models import Pista, Cafeteria,Menu, Reserva, Mensaje, Usuario
from django.utils import timezone
from datetime import time
from django.contrib.auth.forms import UserCreationForm



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
    class Meta:
        model = Reserva
        fields = ['pista', 'fecha', 'hora']

    def clean(self):
        cleaned_data = super().clean()
        pista = cleaned_data.get("pista")
        fecha = cleaned_data.get("fecha")
        hora = cleaned_data.get("hora")

        if fecha < timezone.now().date():
            raise forms.ValidationError("No se puede reservar en fechas pasadas.")

        # Validar que la pista no esté reservada en ese horario
        if Reserva.objects.filter(pista=pista, fecha=fecha, hora=hora).exists():
            raise forms.ValidationError("Esta pista ya está reservada en esa fecha y hora.")

        return cleaned_data

    HORA_CHOICES = [(f"{h:02d}:00", f"{h:02d}:00") for h in range(14, 24)]
    hora = forms.ChoiceField(choices=HORA_CHOICES)


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