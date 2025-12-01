from django import forms

from .models import Pista, Cafeteria,Menu, Reserva, Mensaje, Usuario, Jugador
from django.utils import timezone
from datetime import time, datetime
from django.contrib.auth.forms import UserCreationForm

# --------------------------- REGISTRO DE USUARIO ---------------------------
class RegistroUsuarioForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Se requiere un email válido")

    class Meta:
        model = Usuario
        fields = ("username", "email", "password1", "password2")

# ----------------------------- FORMULARIO PISTA ----------------------------
class PistaForm(forms.ModelForm):
    class Meta:
        model = Pista
        fields = ['id_pista', 'capacidad_maxima', 'tipo_pista', 'estado']

    # Valida que el ID de pista no esté repetido
    def clean_id_pista(self):
        id_pista = self.cleaned_data['id_pista']
        if Pista.objects.filter(id_pista=id_pista).exists():
            raise forms.ValidationError("El número de pista ya existe.")
        return id_pista

# ----------------------------- FORMULARIO RESERVA --------------------------
class ReservaForm(forms.ModelForm):
    # Genera opciones de hora de 14:00 a 23:00
    HORA_CHOICES = [(f"{h:02d}:00", f"{h:02d}:00") for h in range(14, 24)]

    hora = forms.ChoiceField(
        choices=HORA_CHOICES,
        label="Hora",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Reserva
        fields = ['fecha', 'hora', 'pista']

    # Validación general del formulario
    def clean(self):
        cleaned_data = super().clean()
        pista = cleaned_data.get("pista")
        fecha = cleaned_data.get("fecha")
        hora = cleaned_data.get("hora")

        if not fecha or not hora or not pista:
            return cleaned_data

        # Convierte string de hora a objeto time
        if isinstance(hora, str):
            hora = datetime.strptime(hora, "%H:%M").time()
            cleaned_data["hora"] = hora

        # Fecha no puede ser anterior a hoy
        if fecha < timezone.now().date():
            raise forms.ValidationError("No se puede reservar en fechas pasadas.")

        # No puede haber reservas duplicadas
        if Reserva.objects.filter(pista=pista, fecha=fecha, hora=hora).exists():
            raise forms.ValidationError("Esta pista ya está reservada en esa fecha y hora.")

        return cleaned_data

# ------------------------- FORMULARIOS PARA PISTAS -------------------------
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

# ------------------------------ FORMULARIO CONTACTO ------------------------
class ContactoForm(forms.ModelForm):
    class Meta:
        model = Mensaje
        fields = ['nombre', 'email', 'mensaje']

# ------------------------------- FORMULARIO MENU ---------------------------
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

