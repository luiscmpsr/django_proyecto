from django.urls import path
from views import buscador_view

urlpatterns = [
    path("", buscador_view, name="buscador"),
]
