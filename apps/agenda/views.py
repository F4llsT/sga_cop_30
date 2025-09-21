# apps/agenda/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Event, UserAgenda
import json
from django.conf import settings
from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder

# -----------------------------------------------------------------------------
# Views da Agenda (Oficial e Pessoal)
# -----------------------------------------------------------------------------

def agenda_oficial(request):
    """
    Exibe a lista de todos os eventos oficiais.
    """
    eventos = Event.objects.all().order_by('start_time', 'horario')
    
    # Get the list of event IDs that the user has added to their agenda
    user_events = []
    if request.user.is_authenticated:
        user_events = list(UserAgenda.objects.filter(user=request.user).values_list('event_id', flat=True))
    
    context = {
        'eventos': eventos,
        'user_events': user_events
    }
    return render(request, 'agenda/agenda_oficial.html', context)

from datetime import datetime, timedelta
from django.utils import timezone

@login_required
def agenda_pessoal(request):
    """
    Exibe a agenda pessoal do usuário logado.
    Remove automaticamente eventos que já passaram mais de 10 horas do seu início.
    """
    # Remove eventos antigos (mais de 10 horas do início)
    ten_hours_ago = timezone.now() - timedelta(hours=10)
    UserAgenda.objects.filter(
        user=request.user,
        event__start_time__lt=ten_hours_ago
    ).delete()
    
    # Get the user's agenda items, ordered by event start time
    agenda_items = UserAgenda.objects.filter(
        user=request.user
    ).select_related('event').order_by('event__start_time')
    
    context = {
        'agenda_items': agenda_items,
        'title': 'Minha Agenda Pessoal'
    }
    return render(request, 'agenda/agenda_pessoal.html', context)

# -----------------------------------------------------------------------------
# Views de Ações (Adicionar/Remover Eventos)
# -----------------------------------------------------------------------------

@login_required
def add_to_agenda(request, event_id):
    """
    Adiciona um evento à agenda pessoal do usuário.
    """
    evento = get_object_or_404(Event, pk=event_id)
    
    # Verifica se o evento já está na agenda do usuário
    already_added = UserAgenda.objects.filter(user=request.user, event=evento).exists()
    
    if not already_added:
        UserAgenda.objects.create(user=request.user, event=evento)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': 'Evento adicionado à sua agenda!',
            'already_added': already_added
        })
    
    return redirect('agenda:agenda_pessoal')

@login_required
def remove_from_agenda(request, event_id):
    """
    Remove um evento da agenda pessoal do usuário.
    """
    evento = get_object_or_404(Event, pk=event_id)
    UserAgenda.objects.filter(user=request.user, event=evento).delete()
    return redirect('agenda:agenda_pessoal')

# -----------------------------------------------------------------------------
# Views do Mapa
# -----------------------------------------------------------------------------

def mapa_eventos(request):
    """
    Exibe o mapa com todos os eventos que possuem coordenadas.
    """
    eventos = Event.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True)
    eventos_data = [{
        "titulo": evento.titulo,
        "data": evento.start_time,
        "hora": evento.hora,
        "latitude": evento.latitude,
        "longitude": evento.longitude,
        "id": evento.id
    } for evento in eventos]

    context = {
        'eventos_json': json.dumps(list(eventos_data), cls=DjangoJSONEncoder),
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY
    }
    return render(request, 'agenda/mapa_eventos.html', context)

# -----------------------------------------------------------------------------
# View de Detalhes do Evento (com mapa integrado)
# -----------------------------------------------------------------------------

def detalhes_evento(request, event_id):
    """
    Exibe os detalhes de um evento específico, incluindo um mapa se houver localização.
    """
    evento = get_object_or_404(Event, pk=event_id)
    
    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = UserAgenda.objects.filter(user=request.user, event=evento).exists()

    evento_mapa_data = None
    if evento.latitude and evento.longitude:
        evento_mapa_data = {
            "titulo": evento.titulo,
            "latitude": evento.latitude,
            "longitude": evento.longitude,
        }

    context = {
        'evento': evento,
        'is_favorited': is_favorited,
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
        'evento_mapa_json': json.dumps(evento_mapa_data)
    }
    
    return render(request, 'agenda/detalhes_evento.html', context)

# Adicione aqui quaisquer outras views que possam estar faltando no futuro.