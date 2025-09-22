from django.urls import path
from views import buscar_view, solicitud_view, crear_solicitud_view

urlpatterns = [
    path("", buscar_view, name="buscador"),
path('solicitud/', solicitud_view, name='solicitud'),
path('crear_solicitud/', crear_solicitud_view, name='crear_solicitud'),
]
