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
    
    # URL temporária para teste
    path('criar-favoritos-teste/', views.criar_favoritos_teste, name='criar_favoritos_teste'),
    
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
    
    # URLs para CRUD de Eventos
    path('eventos/novo/', views.criar_evento, name='evento_criar'),
    path('eventos/<int:evento_id>/editar/', views.editar_evento, name='evento_editar'),
    path('eventos/<int:evento_id>/excluir/', views.excluir_evento, name='evento_excluir'),
    path('api/eventos/', views.api_eventos, name='evento_listar'),
    path('api/eventos/<int:evento_id>/', views.api_evento_detalhe, name='evento_detalhe'),

    # URLs para Avisos
    path('avisos/', views.avisos_admin, name='avisos_admin'),
    path('avisos/<int:aviso_id>/excluir/', views.excluir_aviso, name='excluir_aviso'),
    path('avisos/<int:aviso_id>/fixar/', views.fixar_aviso, name='fixar_aviso'),
    path('api/avisos/', views.avisos_api, name='avisos_api'),
    
    # Rota para ativar/desativar usuários
    path('api/usuarios/<int:user_id>/toggle-status/', 
         views_usuarios.toggle_user_status, 
         name='toggle_user_status'),
    
    # URLs para gerenciamento de contatos e redes sociais
    path('contatos/', views.contatos_admin, name='contatos_admin'),
    
    # APIs para Redes Sociais
    path('api/redes-sociais/', views.api_redes_sociais, name='api_redes_sociais'),
    path('api/redes-sociais/<int:pk>/', views.api_rede_social_detalhe, name='api_rede_social_detalhe'),
    
    # APIs para Contatos
    path('api/contatos/', views.api_contatos, name='api_contatos'),
    path('api/contatos/<int:pk>/', views.api_contato_detalhe, name='api_contato_detalhe'),
    
    # APIs para Configurações do Site
    path('api/configuracoes-site/', views.api_configuracoes_site, name='api_configuracoes_site'),
    path('api/configuracoes-site/<int:pk>/', views.api_configuracao_detalhe, name='api_configuracao_detalhe'),
]