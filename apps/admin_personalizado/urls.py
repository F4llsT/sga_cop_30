# urls.py
from django.urls import path
from . import views

app_name = 'admin_personalizado'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('passe-facil/', views.passefacil_admin, name='passefacil_admin'),
    path('notificacoes/enviar/', views.enviar_notificacao, name='enviar_notificacao'),
    path('notificacoes/editar/<int:pk>/', views.editar_notificacao, name='editar_notificacao'),
    path('notificacoes/excluir/<int:pk>/', views.excluir_notificacao, name='excluir_notificacao'),
    path('api/notificacoes/enviar/', views.enviar_notificacao_ajax, name='enviar_notificacao_ajax'),
]