from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Notificacao

@login_required
def listar_notificacoes(request):
    """Retorna as notificações do usuário logado"""
    notificacoes = Notificacao.objects.filter(usuario=request.user)
    
    data = {
        'notificacoes': [],
        'total': notificacoes.count(),
        'nao_lidas': notificacoes.filter(lida=False).count()
    }
    
    for notif in notificacoes:
        data['notificacoes'].append({
            'id': notif.id,
            'titulo': notif.titulo,
            'mensagem': notif.mensagem,
            'tipo': notif.tipo,
            'lida': notif.lida,
            'tempo': notif.tempo_decorrido,
            'criada_em': notif.criada_em.isoformat()
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
