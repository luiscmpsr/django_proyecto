# forms.py
from django import forms

ESTADOS = [
    ('Pendiente', 'Pendiente'),
    ('En Revisión', 'En Revisión'),
    ('Aprobado', 'Aprobado'),
    ('Rechazado', 'Rechazado'),
]

class BusquedaForm(forms.Form):
    OPCIONES = [
        ('identificacion', 'Identificación'),
        ('nombre', 'Nombre'),
    ]
    criterio = forms.ChoiceField(choices=OPCIONES, label="Buscar por")
    valor = forms.CharField(max_length=200, label="Ingrese el dato")


class SolicitudForm(forms.Form):
    est_nombre = forms.CharField(label="Nombre del Estudiante", widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    est_identificacion = forms.CharField(label="Identificación", widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    est_carnet = forms.CharField(label="Carnet", required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    est_correo = forms.CharField(label="Correo", required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    est_telefono = forms.CharField(label="Teléfono", required=False, widget=forms.TextInput(attrs={'readonly': 'readonly'}))

    periodo = forms.CharField(label="Periodo del TCU", widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    lugar = forms.CharField(label="Lugar del TCU")
    encargado = forms.CharField(label="Encargado del Estudiante")
    fecha_solicitud = forms.CharField(label="Fecha de Solicitud (DD/MM/AAAA)")
    estado = forms.ChoiceField(label="Estado", choices=ESTADOS)
    observaciones = forms.CharField(label="Observaciones", widget=forms.Textarea)
    # file input, allow multiple files
    documentos = forms.FileField(
        label="Documentos",
        widget=forms.ClearableFileInput(),
        required=False
    )

    def clean_fecha_solicitud(self):
        val = self.cleaned_data.get('fecha_solicitud', '').strip()
        from datetime import datetime
        try:
            datetime.strptime(val, '%d/%m/%Y')
            return val
        except Exception:
            raise forms.ValidationError("Fecha inválida. Formato esperado DD/MM/AAAA")
