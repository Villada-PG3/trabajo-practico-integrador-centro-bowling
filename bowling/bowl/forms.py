from django import forms
from .models import Pista, Cafeteria, Estado, Reserva
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

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
        fields = ['fecha', 'hora', 'cliente', 'pista']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo mostrar pistas libres
        try:
            libre = Estado.objects.get(nombre='libre')
            self.fields['pista'].queryset = Pista.objects.filter(estado=libre)
        except Estado.DoesNotExist:
            self.fields['pista'].queryset = Pista.objects.none()
