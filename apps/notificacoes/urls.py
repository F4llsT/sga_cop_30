from django.urls import path
from . import views
from .views_avisos import (
    ListaAvisosView, CriarAvisoView, EditarAvisoView,
    ExcluirAvisoView, ToggleAvisoStatusView, ArquivoAvisosView
)

app_name = 'notificacoes'

urlpatterns = [
    # URLs existentes
    path('', views.listar_notificacoes, name='listar'),
    path('marcar-todas-lidas/', views.marcar_todas_como_lidas, name='marcar_todas_lidas'),
    path('<int:notificacao_id>/marcar-lida/', views.marcar_como_lida, name='marcar_lida'),
    
    # URLs para gerenciamento de avisos
    path('avisos/', ListaAvisosView.as_view(), name='lista_avisos'),
    path('avisos/novo/', CriarAvisoView.as_view(), name='criar_aviso'),
    path('avisos/editar/<int:pk>/', EditarAvisoView.as_view(), name='editar_aviso'),
    path('avisos/excluir/<int:pk>/', ExcluirAvisoView.as_view(), name='excluir_aviso'),
    path('avisos/toggle-status/<int:pk>/', ToggleAvisoStatusView.as_view(), name='toggle_aviso'),
    path('avisos/arquivo/', ArquivoAvisosView.as_view(), name='arquivo_avisos'),
]
