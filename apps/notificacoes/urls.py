from django.urls import path
from . import views

app_name = 'notificacoes'

urlpatterns = [
    path('', views.listar_notificacoes, name='listar'),
    path('marcar-todas-lidas/', views.marcar_todas_como_lidas, name='marcar_todas_lidas'),
    path('<int:notificacao_id>/marcar-lida/', views.marcar_como_lida, name='marcar_lida'),
]
