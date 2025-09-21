from django.shortcuts import render
from forms import BusquedaForm

def buscador_view(request):
    resultado = None
    if request.method == "POST":
        form = BusquedaForm(request.POST)
        if form.is_valid():
            criterio = form.cleaned_data["criterio"]
            valor = form.cleaned_data["valor"]
            # Conectar con Odoo
            resultado = f"Se buscó por {criterio} con el valor: {valor}"
    else:
        form = BusquedaForm()

    return render(request, "buscador_form.html", {"form": form, "resultado": resultado})
