from django.urls import path
from views import buscar_view, solicitud_view

urlpatterns = [
    path("", buscar_view, name="buscador"),
path('solicitud/', solicitud_view, name='solicitud'),
]
