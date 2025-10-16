from django.urls import path, include
from django.views.generic import TemplateView
from . import views
from . import views_usuarios

app_name = 'admin_personalizado'

urlpatterns = [
    # URLs principais
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('passe-facil/', views.passefacil_admin, name='passefacil_admin'),
    path('eventos/', views.eventos_admin, name='eventos_admin'),
    
    # URLs de notificações
    path('notificacoes/enviar/', views.enviar_notificacao, name='enviar_notificacao'),
    path('notificacoes/editar/<int:pk>/', views.editar_notificacao, name='editar_notificacao'),
    path('notificacoes/excluir/<int:pk>/', views.excluir_notificacao, name='excluir_notificacao'),
    path('api/notificacoes/enviar/', views.enviar_notificacao_ajax, name='enviar_notificacao_ajax'),
    
    # URLs de autenticação
    path('accounts/', include('django.contrib.auth.urls')),  # Para autenticação padrão do Django
    path('acesso-negado/', TemplateView.as_view(template_name='admin_personalizado/erros/acesso_negado.html'), name='acesso_negado'),
    
    # URLs de gerenciamento de usuários
    path('usuarios/', views_usuarios.listar_usuarios, name='listar_usuarios'),
    path('usuarios/<int:user_id>/', views_usuarios.detalhes_usuario, name='detalhes_usuario'),
    path('usuarios/<int:user_id>/atualizar/', views_usuarios.atualizar_usuario, name='atualizar_usuario'),
    path('usuarios/<int:user_id>/alterar-papel/', 
         views_usuarios.alterar_papel_usuario, 
         name='alterar_papel'),
    path('api/usuarios/<int:user_id>/atualizar-papel/', 
         views_usuarios.atualizar_papel_usuario, 
         name='atualizar_papel_usuario'),
]