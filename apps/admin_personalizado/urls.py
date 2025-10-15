# urls.py
from django.urls import path
from . import views
from . import views_usuarios

app_name = 'admin_personalizado'

urlpatterns = [
    # URLs principais
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('passe-facil/', views.passefacil_admin, name='passefacil_admin'),
    
    # URLs de notificações
    path('notificacoes/enviar/', views.enviar_notificacao, name='enviar_notificacao'),
    path('notificacoes/editar/<int:pk>/', views.editar_notificacao, name='editar_notificacao'),
    path('notificacoes/excluir/<int:pk>/', views.excluir_notificacao, name='excluir_notificacao'),
    path('api/notificacoes/enviar/', views.enviar_notificacao_ajax, name='enviar_notificacao_ajax'),
    
    # URLs de gerenciamento de usuários
    path('usuarios/', views_usuarios.listar_usuarios, name='usuarios'),
    path('api/usuarios/<int:user_id>/atualizar-papel/', 
         views_usuarios.atualizar_papel_usuario, 
         name='atualizar_papel_usuario'),
]