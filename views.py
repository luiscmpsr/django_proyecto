# views.py
import requests, json
from django.shortcuts import render, redirect
from django.urls import reverse
from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest
from forms import BusquedaForm, SolicitudForm

# URLs a tus endpoints Odoo
ODOO_BASE = "http://localhost:8069"
ODOO_API_ESTUDIANTE = f"{ODOO_BASE}/api/estudiante_api"
ODOO_API_GET_PERIODOS = f"{ODOO_BASE}/api/get_periodos_api"
ODOO_API_GET_PERIODOINFO = f"{ODOO_BASE}/api/get_periodoinfo_api"
ODOO_API_CREAR_SOLICITUD = f"{ODOO_BASE}/api/crear_solicitud_api"


def buscar_view(request):
    """
    Página inicial con buscador.
    POST -> consulta Odoo (server-side). Si encuentra, redirige a /solicitud/?identificacion=...
    """
    mensaje = None
    if request.method == "POST":
        form = BusquedaForm(request.POST)
        if form.is_valid():
            criterio = form.cleaned_data['criterio']
            valor = form.cleaned_data['valor']

            params = {criterio: valor}
            try:
                resp = requests.get(ODOO_API_ESTUDIANTE, params=params, timeout=8)
                if resp.status_code == 200:
                    data = resp.json()
                    # si el API devuelve lista o dict? suponemos dict con est_identificacion o lista -> adaptamos:
                    if isinstance(data, list):
                        if len(data) == 0:
                            mensaje = "Estudiante no encontrado."
                        else:
                            estudiante = data[0]
                            return redirect(reverse('solicitud') + f"?identificacion={estudiante.get('est_identificacion')}")
                    elif isinstance(data, dict):
                        if data.get('error'):
                            mensaje = data.get('error')
                        else:
                            # redirige con la identificación
                            return redirect(reverse('solicitud') + f"?identificacion={data.get('est_identificacion')}")
                    else:
                        mensaje = "Respuesta inesperada del API."
                else:
                    mensaje = f"Error del API ({resp.status_code})"
            except Exception as e:
                mensaje = f"Error conectando con el API: {e}"
    else:
        form = BusquedaForm()

    return render(request, "buscar.html", {"form": form, "mensaje": mensaje})


def solicitud_view(request):
    """
    Muestra la página de solicitud. Lee ?identificacion=xxx y consulta Odoo para obtener
    datos del estudiante y la lista de periodos (proxy).
    """
    identificacion = request.GET.get('identificacion')
    if not identificacion:
        return redirect('buscar')

    # obtener estudiante
    try:
        resp = requests.get(ODOO_API_ESTUDIANTE, params={'identificacion': identificacion}, timeout=8)
        student_data = {}
        if resp.status_code == 200:
            d = resp.json()
            # soportar dict o lista
            if isinstance(d, list):
                student_data = d[0] if d else {}
            elif isinstance(d, dict):
                if d.get('error'):
                    return render(request, "solicitud.html", {"error": d.get('error')})
                student_data = d
        else:
            return render(request, "solicitud.html", {"error": f"Error al obtener estudiante ({resp.status_code})"})
    except Exception as e:
        return render(request, "solicitud.html", {"error": f"Error conectando con API: {e}"})

    # obtener lista de periodos (nombres)
    periodos = []
    try:
        resp2 = requests.get(ODOO_API_GET_PERIODOS, timeout=8)
        if resp2.status_code == 200:
            periodos = resp2.json()  # suponemos una lista de strings o dicts con name
        else:
            periodos = []
    except Exception:
        periodos = []

    # prellenar el formulario de solicitud parcialmente
    initial = {
        'est_nombre': student_data.get('est_nombre', ''),
        'est_identificacion': student_data.get('est_identificacion', ''),
        'est_carnet': student_data.get('est_carnet', ''),
        'est_correo': student_data.get('est_correo', ''),
        'est_telefono': student_data.get('est_telefono', ''),
        'periodo': '',
    }
    form = SolicitudForm(initial=initial)

    return render(request, "solicitud.html", {
        "form": form,
        "student": student_data,
        "periodos": periodos,
    })


def crear_solicitud_view(request):
    """
    Endpoint Django que recibe POST con todos los campos y archivos,
    valida y reenvía a Odoo (crear_solicitud_api). Devuelve JSON al frontend.
    """
    if request.method != "POST":
        return HttpResponseBadRequest("Método no permitido")

    form = SolicitudForm(request.POST, request.FILES)
    if not form.is_valid():
        # devolver errores como texto legible
        errors = []
        for f, err in form.errors.items():
            errors.append(f"{f}: {', '.join(err)}")
        return JsonResponse({"resultado": "error", "detalle": " ; ".join(errors)})

    # Validaciones extra: al menos un archivo
    archivos = request.FILES.getlist('documentos')
    if len(archivos) == 0:
        return JsonResponse({"resultado": "error", "detalle": "Debe adjuntar al menos un archivo."})

    # preparar payload para Odoo
    payload = {
        "nombre": form.cleaned_data['est_nombre'],
        "identificacion": form.cleaned_data['est_identificacion'],
        "carnet": form.cleaned_data.get('est_carnet', ''),
        "correo": form.cleaned_data.get('est_correo', ''),
        "telefono": form.cleaned_data.get('est_telefono', ''),
        "periodo": form.cleaned_data['periodo'],
        "lugar": form.cleaned_data['lugar'],
        "encargado": form.cleaned_data['encargado'],
        "fecha_solicitud": form.cleaned_data['fecha_solicitud'],
        "estado": form.cleaned_data['estado'],
        "observaciones": form.cleaned_data['observaciones'],
    }

    # Enviar archivos como multipart/form-data junto con payload JSON
    files = []
    for idx, f in enumerate(archivos):
        # f.name, f.read()
        # requests requires tuple (fieldname, (filename, fileobj, content_type))
        files.append(('documentos', (f.name, f.read(), f.content_type or 'application/octet-stream')))

    # Mandar a Odoo
    try:
        # enviamos payload como campo 'data' JSON + archivos
        multipart = {
            'data': (None, json.dumps(payload), 'application/json'),
        }
        # build files for requests: multipart + files
        # using requests-toolbelt would be nicer but plain requests works
        # prepare final files param
        files_param = []
        for key, val in multipart.items():
            files_param.append((key, val))
        for file_tuple in files:
            files_param.append(file_tuple)

        od_resp = requests.post(ODOO_API_CREAR_SOLICITUD, files=files_param, timeout=20)
        if od_resp.status_code == 200:
            od_json = od_resp.json()
            return JsonResponse(od_json)
        else:
            return JsonResponse({"resultado": "error", "detalle": f"API Odoo respondió {od_resp.status_code}"})
    except Exception as e:
        return JsonResponse({"resultado": "error", "detalle": f"Error conectando con API: {e}"})
