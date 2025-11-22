from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
import json
from .models import Notificacao, NotificacaoUsuario

@login_required
def listar_notificacoes(request):
    """Retorna as notificações do usuário logado com menos de 10 horas"""
    # Calcular o limite de 10 horas atrás
    dez_horas_atras = timezone.now() - timedelta(hours=10)
    
    # Obter as notificações do usuário com menos de 10 horas
    notificacoes_usuario = request.user.notificacoes_usuario.filter(
        notificacao__criada_em__gte=dez_horas_atras
    ).select_related('notificacao').order_by('-notificacao__criada_em')
    
    # Preparar a lista de notificações com status de leitura
    notificacoes_data = []
    for rel_usuario in notificacoes_usuario:
        notif = rel_usuario.notificacao
        notificacoes_data.append({
            'id': notif.id,
            'titulo': notif.titulo,
            'mensagem': notif.mensagem,
            'tipo': notif.tipo,
            'lida': rel_usuario.lida,
            'tempo': rel_usuario.tempo_decorrido if hasattr(rel_usuario, 'tempo_decorrido') else 'agora mesmo',
            'criada_em': notif.criada_em.isoformat(),
            'evento_id': notif.evento.id if notif.evento else None
        })
    
    # Contar notificações não lidas
    nao_lidas = sum(1 for n in notificacoes_data if not n['lida'])
    
    data = {
        'notificacoes': notificacoes_data,
        'total': len(notificacoes_data),
        'nao_lidas': nao_lidas
    }
    
    return JsonResponse(data)

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def marcar_todas_como_lidas(request):
    """Marca todas as notificações do usuário como lidas"""
    try:
        # Atualiza todas as notificações não lidas do usuário
        notificacoes_nao_lidas = NotificacaoUsuario.objects.filter(
            usuario=request.user,
            lida=False
        )
        
        count = notificacoes_nao_lidas.count()
        
        # Atualiza o status para lido e define a data/hora atual
        notificacoes_nao_lidas.update(
            lida=True,
            lida_em=timezone.now()
        )
        
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
        # Obtém a relação de notificação do usuário
        notificacao_usuario = NotificacaoUsuario.objects.get(
            notificacao_id=notificacao_id,
            usuario=request.user
        )
        
        # Marca como lida se ainda não estiver
        if not notificacao_usuario.lida:
            notificacao_usuario.lida = True
            notificacao_usuario.lida_em = timezone.now()
            notificacao_usuario.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Notificação marcada como lida'
        })
    except NotificacaoUsuario.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Notificação não encontrada ou você não tem permissão para acessá-la'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao marcar notificação: {str(e)}'
        }, status=500)
