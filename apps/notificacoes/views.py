from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
import json
from .models import Notificacao

@login_required
def listar_notificacoes(request):
    """Retorna as notificações do usuário logado com menos de 10 horas"""
    # Calcular o limite de 10 horas atrás
    dez_horas_atras = timezone.now() - timedelta(hours=10)
    
    # Filtrar notificações do usuário com menos de 10 horas
    notificacoes = Notificacao.objects.filter(
        usuario=request.user,
        criada_em__gte=dez_horas_atras
    ).order_by('-criada_em')  # Ordena do mais recente para o mais antigo
    
    # Contar notificações não lidas (apenas as últimas 10 horas)
    nao_lidas = notificacoes.filter(lida=False).count()
    
    data = {
        'notificacoes': [],
        'total': notificacoes.count(),
        'nao_lidas': nao_lidas
    }
    
    for notif in notificacoes:
        data['notificacoes'].append({
            'id': notif.id,
            'titulo': notif.titulo,
            'mensagem': notif.mensagem,
            'tipo': notif.tipo,
            'lida': notif.lida,
            'tempo': notif.tempo_decorrido,
            'criada_em': notif.criada_em.isoformat(),
            'evento_id': notif.evento.id if notif.evento else None
        })
    
    return JsonResponse(data)

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def marcar_todas_como_lidas(request):
    """Marca todas as notificações do usuário como lidas"""
    try:
        notificacoes_nao_lidas = Notificacao.objects.filter(
            usuario=request.user, 
            lida=False
        )
        
        count = notificacoes_nao_lidas.count()
        notificacoes_nao_lidas.update(lida=True)
        
        return JsonResponse({
            'success': True,
            'message': f'{count} notificação(ões) marcada(s) como lida(s)',
            'count': count
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao marcar notificações: {str(e)}'
        }, status=500)

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def marcar_como_lida(request, notificacao_id):
    """Marca uma notificação específica como lida"""
    try:
        notificacao = Notificacao.objects.get(
            id=notificacao_id,
            usuario=request.user
        )
        notificacao.marcar_como_lida()
        
        return JsonResponse({
            'success': True,
            'message': 'Notificação marcada como lida'
        })
    except Notificacao.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Notificação não encontrada'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao marcar notificação: {str(e)}'
        }, status=500)
