from django import forms

class BusquedaForm(forms.Form):
    OPCIONES = [
        ('identificacion', 'Identificación'),
        ('nombre',         'Nombre'),
    ]
    criterio = forms.ChoiceField(choices=OPCIONES, label="Buscar por:")
    valor    = forms.CharField(max_length=100, label="Ingrese el dato:")
