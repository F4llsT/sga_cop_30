from django.db import models
from django.utils import timezone
from .models import Aviso

def avisos_ativos(request):
    """
    Context processor para adicionar avisos ativos a todos os templates.
    """
    if not hasattr(request, 'user') or not request.user.is_authenticated:
        return {}
        
    # Buscar avisos ativos e não expirados, ordenados por fixo no topo e data de criação
    avisos = Aviso.objects.filter(
        ativo=True
    ).filter(
        models.Q(data_expiracao__isnull=True) | models.Q(data_expiracao__gt=timezone.now())
    ).order_by('-fixo_no_topo', '-data_criacao')
    
    return {
        'avisos_ativos': avisos
    }
