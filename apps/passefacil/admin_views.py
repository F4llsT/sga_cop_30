# apps/passefacil/admin_views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.utils import timezone
from .models import PasseFacil, ValidacaoQRCode
from django.contrib import messages
from django.db.models import Count
from datetime import timedelta

def is_admin(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(is_admin)
def admin_dashboard(request):
    # Últimas 10 validações
    validacoes_recentes = ValidacaoQRCode.objects.select_related(
        'passe_facil__user'
    ).order_by('-data_validacao')[:10]
    
    # Estatísticas
    agora = timezone.now()
    hoje = agora.date()
    inicio_dia = timezone.make_aware(timezone.datetime.combine(hoje, timezone.datetime.min.time()))
    
    total_validacoes = ValidacaoQRCode.objects.filter(
        data_validacao__gte=inicio_dia
    ).count()
    
    validas = ValidacaoQRCode.objects.filter(
        valido=True,
        data_validacao__gte=inicio_dia
    ).count()
    
    invalidas = total_validacoes - validas
    
    # Adiciona o CSRF token ao contexto
    from django.template.context_processors import csrf
    context = {
        'validacoes_recentes': validacoes_recentes,
        'total_validacoes': total_validacoes,
        'validas': validas,
        'invalidas': invalidas,
        'ultimas_validacoes': validacoes_recentes,  # Adiciona para compatibilidade com o template
    }
    # Adiciona o token CSRF ao contexto
    context.update(csrf(request))
    return render(request, 'passefacil/admin/dashboard.html', context)

@user_passes_test(is_admin)
def validar_qr_code(request):
    if request.method != 'POST':
        return JsonResponse({'erro': 'Método não permitido'}, status=405)
    
    # Verifica se o código foi fornecido
    codigo = request.POST.get('codigo')
    if not codigo:
        return JsonResponse({
            'valido': False, 
            'erro': 'Código não fornecido',
            'data_validacao': timezone.now().strftime('%d/%m/%Y %H:%M:%S')
        }, status=400)
    
    # Remove espaços em branco extras
    codigo = codigo.strip()
    
    try:
        # Tenta encontrar o passe com o código fornecido
        try:
            passe = PasseFacil.objects.get(codigo=codigo)
        except PasseFacil.DoesNotExist:
            # Registra tentativa inválida
            ValidacaoQRCode.objects.create(
                codigo=codigo,
                valido=False,
                ip_address=request.META.get('REMOTE_ADDR', '0.0.0.0')
            )
            return JsonResponse({
                'valido': False, 
                'erro': 'Código não encontrado',
                'codigo': codigo,
                'data_validacao': timezone.now().strftime('%d/%m/%Y %H:%M:%S')
            }, status=404)
        
        # Verifica se o passe está ativo
        if not passe.ativo:
            # Registra tentativa de uso de passe inativo
            ValidacaoQRCode.objects.create(
                passe_facil=passe,
                codigo=codigo,
                valido=False,
                ip_address=request.META.get('REMOTE_ADDR', '0.0.0.0'),
                observacoes='Tentativa de uso de passe inativo'
            )
            return JsonResponse({
                'valido': False, 
                'erro': 'Este passe está inativo',
                'codigo': codigo,
                'data_validacao': timezone.now().strftime('%d/%m/%Y %H:%M:%S')
            }, status=403)
        
        # Cria o registro de validação
        validacao = ValidacaoQRCode(
            passe_facil=passe,
            codigo=codigo,
            valido=True,
            ip_address=request.META.get('REMOTE_ADDR', '0.0.0.0')
        )
        validacao.save()
        
        # Atualiza a data de atualização do passe
        passe.data_atualizacao = timezone.now()
        passe.save()
        
        # Prepara os dados do usuário para a resposta
        usuario_nome = str(passe.user.get_full_name() or passe.user.username)
        
        return JsonResponse({
            'valido': True,
            'mensagem': f'Passe válido para {usuario_nome}',
            'usuario': {
                'nome': usuario_nome,
                'email': passe.user.email,
                'id': passe.user.id
            },
            'codigo': codigo,
            'validacao_id': validacao.id,
            'data_validacao': validacao.data_validacao.strftime('%d/%m/%Y %H:%M:%S')
        })
        
    except Exception as e:
        # Log do erro para debug
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Erro ao validar QR Code: {str(e)}', exc_info=True)
        
        # Resposta genérica de erro
        return JsonResponse({
            'valido': False,
            'erro': 'Erro interno ao processar a validação',
            'detail': str(e),
            'data_validacao': timezone.now().strftime('%d/%m/%Y %H:%M:%S')
        }, status=500)