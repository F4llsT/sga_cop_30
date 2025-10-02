from django.urls import path
from . import views

app_name = 'admin_personalizado'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('passe-facil/', views.passefacil_admin, name='passefacil_admin'),
    # Adicione outras URLs conforme necessário
]