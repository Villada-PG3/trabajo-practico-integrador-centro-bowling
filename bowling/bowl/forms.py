from django import forms
from .models import Pista, Menu

class PistaForm(forms.ModelForm):
    class Meta:
        model = Pista
        fields = ['id_pista', 'capacidad_maxima', 'tipo_pista', 'estado']

    def clean_numero(self):
        id_pista = self.cleaned_data['id_pista']
        if Pista.objects.filter(id_pista=id_pista).exists():
            raise forms.ValidationError("El número de pista ya existe.")
        return id_pista
class CafeteriaForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = ['id_menu', 'nombre', 'tipo_pista', 'estado']

    def clean_numero(self):
        id_pista = self.cleaned_data['id_pista']
        if Pista.objects.filter(id_pista=id_pista).exists():
            raise forms.ValidationError("El número de pista ya existe.")
        return id_pista