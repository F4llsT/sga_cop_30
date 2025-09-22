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
    
    # Lista todos os passes com suas últimas validações
    ultimas_validacoes_subquery = ValidacaoQRCode.objects.filter(
        passe_facil_id=OuterRef('pk')
    ).order_by('-data_validacao').values('id')[:1]
    
    passes = PasseFacil.objects.select_related('user').prefetch_related(
        Prefetch(
            'validacoes',
            queryset=ValidacaoQRCode.objects.filter(
                id__in=Subquery(ultimas_validacoes_subquery)
            ),
            to_attr='ultimas_validacoes'
        )
    ).order_by('user__first_name', 'user__last_name')
    
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
        'passes': passes,  # Adiciona a lista de passes ao contexto
        'total_validacoes': total_validacoes,
        'validas': validas,
        'invalidas': invalidas,
        'ultimas_validacoes': validacoes_recentes,
    }
    # Adiciona o token CSRF ao contexto
    context.update(csrf(request))
    return render(request, 'passefacil/admin/dashboard.html', context)

from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def validar_qr_code(request):
    """
    View para validação de QR Code no painel de administração.
    Suporta tanto requisições AJAX quanto requisições normais.
    """
    if request.method == 'GET':
        # Exibe o formulário de validação
        return render(request, 'admin/passefacil/validar_qr_code.html', {
            'title': 'Validar QR Code',
            'opts': PasseFacil._meta,
            'has_permission': True,
        })
    
    # Para requisições POST (validação do código)
    codigo = request.POST.get('codigo', '').strip()
    
    if not codigo:
        messages.error(request, 'Nenhum código foi fornecido.')
        return redirect('admin:passefacil_validar_qr_code')
    
    try:
        try:
            passe = PasseFacil.objects.get(codigo=codigo)
        except PasseFacil.DoesNotExist:
            # Registra tentativa inválida
            ValidacaoQRCode.objects.create(
                codigo=codigo,
                valido=False,
                ip_address=request.META.get('REMOTE_ADDR', '0.0.0.0'),
                observacoes='Código não encontrado'
            )
            messages.error(request, f'Código não encontrado: {codigo}')
            return redirect('admin:passefacil_validar_qr_code')
        
        # Verifica se o passe está ativo
        if not passe.ativo:
            ValidacaoQRCode.objects.create(
                passe_facil=passe,
                codigo=codigo,
                valido=False,
                ip_address=request.META.get('REMOTE_ADDR', '0.0.0.0'),
                observacoes='Tentativa de uso de passe inativo'
            )
            messages.error(request, f'Passe inativo para o código: {codigo}')
            return redirect('admin:passefacil_validar_qr_code')
        
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
        
        # Prepara a mensagem de sucesso
        usuario_nome = passe.user.get_full_name() or passe.user.username
        messages.success(
            request, 
            f'Validação realizada com sucesso para: {usuario_nome} (Código: {codigo})',
            extra_tags='success'
        )
        
        # Se for uma requisição AJAX, retorna JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
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
            
        return redirect('admin:passefacil_validar_qr_code')
        
    except Exception as e:
        # Log do erro para debug
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'Erro ao validar QR Code: {str(e)}', exc_info=True)
        
        error_msg = f'Erro ao processar a validação: {str(e)}'
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'valido': False,
                'erro': 'Erro ao processar a validação',
                'detail': str(e)
            }, status=500)
            
        messages.error(request, error_msg)
        return redirect('admin:passefacil_validar_qr_code')