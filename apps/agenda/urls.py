from django.urls import path
from . import views

app_name = 'agenda'
urlpatterns = [
    path('', views.agenda_oficial, name='agenda_oficial'),
    path('minha_agenda/', views.agenda_pessoal, name='agenda_pessoal'),
    path('add/<int:event_id>/', views.add_to_agenda, name='add_to_agenda'),
    # Adicionando a nova URL para remover eventos
    path('remove/<int:event_id>/', views.remove_from_agenda, name='remove_from_agenda'),
    # URL para detalhes do evento
    path('evento/<int:event_id>/', views.detalhes_evento, name='detalhes_evento'),
    path('mapa/', views.mapa_eventos, name='mapa_eventos'),
]




