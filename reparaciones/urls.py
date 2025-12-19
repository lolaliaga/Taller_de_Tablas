from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('crear/', views.crear_reparacion, name='crear_reparacion'),
    path('registrar/', views.registrar, name='registrar'),
]
