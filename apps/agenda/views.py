from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import Event, UserAgenda

def agenda_oficial(request):
    """
    Exibe a agenda oficial com todos os eventos e permite filtrar por tema.
    Acesso público, não requer autenticação.
    """
    # Usa o manager personalizado que filtra eventos antigos
    eventos = Event.objects.all().order_by('start_time')
    user_events = []
    
    # Se o usuário estiver autenticado, carrega seus eventos
    if request.user.is_authenticated:
        user_events = list(UserAgenda.objects.filter(
            user=request.user,
            event__in=eventos  # Só mostra eventos que ainda estão visíveis
        ).values_list('event_id', flat=True))

    theme_filter = request.GET.get('theme', '')
    if theme_filter:
        eventos = eventos.filter(tags__icontains=theme_filter)

    return render(request, 'agenda/agenda_oficial.html', {
        'eventos': eventos,
        'user_events': user_events,
        'theme_filter': theme_filter,
        'now': timezone.now(),
    })

@login_required
def add_to_agenda(request, event_id):
    """
    Adiciona um evento à agenda pessoal do usuário.
    """
    # Usa o manager personalizado para evitar adicionar eventos antigos
    event = get_object_or_404(Event.all_objects, pk=event_id)
    
    # Verifica se o evento ainda é válido (não passou mais de 10 horas)
    if event.is_past_event:
        messages.error(request, 'Não é possível adicionar eventos que já passaram há mais de 10 horas.')
        return redirect('agenda:agenda_oficial')
    
    # Verifica se o evento já existe na agenda do usuário para evitar duplicatas
    if not UserAgenda.objects.filter(user=request.user, event=event).exists():
        UserAgenda.objects.create(user=request.user, event=event)
        messages.success(request, f'O evento "{event.titulo}" foi adicionado à sua agenda pessoal.')
    else:
        messages.info(request, f'O evento "{event.titulo}" já está na sua agenda.')
    
    return redirect('agenda:agenda_oficial')

@login_required
def agenda_pessoal(request):
    """
    Exibe a agenda pessoal com os eventos favoritados pelo usuário.
    Filtra automaticamente eventos com mais de 10 horas.
    """
    # Filtra os eventos favoritados para o usuário logado
    # Usa o manager personalizado para filtrar eventos antigos
    ten_hours_ago = timezone.now() - timedelta(hours=10)
    agenda_items = UserAgenda.objects.filter(
        user=request.user,
        event__start_time__gte=ten_hours_ago
    ).order_by('event__start_time')
    
    return render(request, 'agenda/agenda_pessoal.html', {
        'agenda_items': agenda_items,
        'now': timezone.now(),
    })

@login_required
def remove_from_agenda(request, event_id):
    """
    Remove um evento da agenda pessoal do usuário.
    """
    # Garantir que a requisição é do tipo POST para segurança
    if request.method == 'POST':
        # Usa o manager all_objects para encontrar o evento mesmo que seja antigo
        agenda_item = get_object_or_404(
            UserAgenda, 
            user=request.user, 
            event_id=event_id
        )
        # Deleta o item
        agenda_item.delete()
        messages.success(request, 'Evento removido da sua agenda pessoal com sucesso.')
    # Redireciona de volta para a agenda pessoal
    return redirect('agenda:agenda_pessoal')

@login_required
def detalhes_evento(request, event_id):
    """
    Exibe os detalhes de um evento específico.
    """
    # Usa o manager personalizado para permitir visualização de eventos antigos
    evento = get_object_or_404(Event.all_objects, pk=event_id)
    
    # Verifica se o evento está na agenda do usuário
    is_favorited = UserAgenda.objects.filter(
        user=request.user, 
        event=evento
    ).exists()
    
    return render(request, 'agenda/detalhes_evento.html', {
        'evento': evento,
        'is_favorited': is_favorited,
        'is_past_event': evento.is_past_event,
    })

def event_detail(request, event_id):
    """
    Exibe os detalhes de um evento específico.
    """
    # Busca o evento pelo ID ou retorna um erro 404 se não for encontrado
    event = get_object_or_404(Event, id=event_id)
    
    # Verifica se o evento está na agenda pessoal do usuário
    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = UserAgenda.objects.filter(user=request.user, event=event).exists()

    context = {
        'event': event,
        'is_favorited': is_favorited
    }
    
    return render(request, 'agenda/detalhes_evento.html', context)