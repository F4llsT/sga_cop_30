# apps/passefacil/urls.py
from django.urls import path
from . import views

app_name = 'passefacil'

urlpatterns = [
    path('', views.passe_facil_view, name='passe_facil'),
    path('atualizar-qr/', views.atualizar_qr_code, name='atualizar_qr_code'),
]