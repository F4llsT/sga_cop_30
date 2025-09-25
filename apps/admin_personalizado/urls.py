from django.urls import path
from . import views

app_name = 'admin_personalizado'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    # Adicione outras URLs conforme necessário
]