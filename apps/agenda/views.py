# apps/agenda/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
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
    Exibe a lista de todos os eventos oficiais com paginação e filtros.
    Mostra 15 eventos por página.
    """
    # Obtém os parâmetros de busca
    search_query = request.GET.get('search', '')
    tag_filter = request.GET.get('tag', '')
    
    # Filtra os eventos
    eventos_list = Event.objects.all().order_by('start_time')
    
    # Aplica filtro de busca no título e descrição
    if search_query:
        from django.db.models import Q
        eventos_list = eventos_list.filter(
            Q(titulo__icontains=search_query) | 
            Q(descricao__icontains=search_query) |
            Q(palestrante__icontains=search_query) |
            Q(local__icontains=search_query)
        )
    
    # Aplica filtro de tag
    if tag_filter:
        eventos_list = eventos_list.filter(tags__icontains=tag_filter)
    
    # Configura a paginação com 15 itens por página
    paginator = Paginator(eventos_list, 15)
    page = request.GET.get('page')
    
    try:
        eventos = paginator.page(page)
    except PageNotAnInteger:
        eventos = paginator.page(1)
    except EmptyPage:
        eventos = paginator.page(paginator.num_pages)
    
    # Obtém a lista de eventos na agenda do usuário
    user_events = []
    if request.user.is_authenticated:
        user_events = list(UserAgenda.objects.filter(
            user=request.user, 
            event__in=eventos.object_list
        ).values_list('event_id', flat=True))
    
    # Obtém todas as tags únicas para o filtro
    all_tags = Event.objects.exclude(tags__isnull=True).exclude(tags__exact='').values_list('tags', flat=True).distinct()
    unique_tags = set()
    for tags in all_tags:
        if tags:  # Verifica se tags não está vazio
            # Divide as tags por vírgula e adiciona ao conjunto
            unique_tags.update(tag.strip() for tag in tags.split(','))
    
    context = {
        'eventos': eventos,
        'user_events': user_events,
        'search_query': search_query,
        'tag_filter': tag_filter,
        'all_tags': sorted(unique_tags)  # Tags únicas ordenadas
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
    # Filtra eventos com coordenadas válidas
    eventos = Event.objects.exclude(latitude__isnull=True).exclude(longitude__isnull=True)
    
    # Formata os dados dos eventos para o mapa
    eventos_data = []
    for evento in eventos:
        # Formata a data e hora de forma mais legível
        data_formatada = evento.start_time.strftime('%d/%m/%Y') if evento.start_time else ''
        hora_formatada = evento.start_time.strftime('%H:%M') if evento.start_time else ''
        
        eventos_data.append({
            "titulo": evento.titulo,
            "data": data_formatada,
            "hora": hora_formatada,
            # Converte Decimal para float para serialização JSON
            "latitude": float(evento.latitude) if evento.latitude is not None else None,
            "longitude": float(evento.longitude) if evento.longitude is not None else None,
            "id": evento.id
        })

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
    if evento.latitude is not None and evento.longitude is not None:
        evento_mapa_data = {
            "titulo": evento.titulo,
            # Converte Decimal para float para serialização JSON
            "latitude": float(evento.latitude) if evento.latitude is not None else None,
            "longitude": float(evento.longitude) if evento.longitude is not None else None,
        }

    context = {
        'evento': evento,
        'is_favorited': is_favorited,
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
        'evento_mapa_json': json.dumps(evento_mapa_data, cls=DjangoJSONEncoder) if evento_mapa_data else 'null'
    }
    
    return render(request, 'agenda/detalhes_evento.html', context)

# Adicione aqui quaisquer outras views que possam estar faltando no futuro.
