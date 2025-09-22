# apps/passefacil/urls.py
from django.urls import path
from . import views

app_name = 'passefacil'

urlpatterns = [
    path('', views.meu_qr_code_view, name='meu_qr_code'),
    path('gerar-qr-code/', views.gerar_qr_code_dinamico, name='gerar_qr_code_dinamico'),
    
    # URL da API para o scanner (usada pelo frontend)
    path('api/validar-qr-code/', views.validar_qr_code, name='api_validar_qr_code'),
]