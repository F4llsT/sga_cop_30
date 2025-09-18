# apps/passefacil/urls.py
from django.urls import path
from . import views
from . import admin_views

app_name = 'passefacil'

urlpatterns = [
    path('', views.passe_facil_view, name='passe_facil'),
    path('atualizar-qr/', views.atualizar_qr_code, name='atualizar_qr_code'),
    
    # URLs do painel de administração
    path('admin/dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('admin/validar-qr/', admin_views.validar_qr_code, name='validar_qr_code'),
]