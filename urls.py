# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.buscar_view, name='buscar'),
    path('buscar/', views.buscar_view, name='buscar'),
    path('solicitud/', views.solicitud_view, name='solicitud'),
    path('crear_solicitud/', views.crear_solicitud_view, name='crear_solicitud'),
]
