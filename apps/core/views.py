from django.shortcuts import render
from django.http import HttpResponse
from apps.agenda.models import Event
from django.utils import timezone

def pagina_inicial(request):
    """
    Busca os próximos 3 eventos e os exibe na página inicial.
    """
    # 1. Filtra eventos cuja data/hora de início é maior ou igual a agora
    # 2. Ordena pelo mais próximo primeiro
    # 3. Limita o resultado aos 3 primeiros eventos
    eventos_futuros = Event.objects.filter(
        start_time__gte=timezone.now()
    ).order_by('start_time')[:4]

    # Cria o contexto para enviar os dados ao template
    context = {
        'proximos_eventos': eventos_futuros
    }
    
    # Renderiza o template, passando o contexto
    return render(request, 'home.html', context)