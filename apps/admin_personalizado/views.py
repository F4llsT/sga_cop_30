from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Count, Q, OuterRef, Subquery, Prefetch
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import transaction
from datetime import timedelta

from apps.passefacil.models import PasseFacil, ValidacaoQRCode
from apps.agenda.models import UserAgenda, Event
from apps.notificacoes.models import Notificacao
from .models import NotificacaoPersonalizada

@staff_member_required
@login_required
def dashboard(request):
    User = get_user_model()

    # Métricas básicas
    total_users = User.objects.count()
    today = timezone.localdate()
    active_today = User.objects.filter(last_login__date=today).count()

    # Filtro de período (apenas para os favoritos/eventos)
    period = request.GET.get("period", "today")  # today | 7d | 30d
    now = timezone.now()
    if period == "7d":
        start_dt = now - timedelta(days=7)
        period_label = "Últimos 7 dias"
    elif period == "30d":
        start_dt = now - timedelta(days=30)
        period_label = "Últimos 30 dias"
    else:
        # today como padrão
        start_dt = now.replace(hour=0, minute=0, second=0, microsecond=0)
        period_label = "Hoje"

    # Agregação de favoritos por evento (usando UserAgenda)
    favoritos_qs = (
        UserAgenda.objects.filter(added_at__gte=start_dt)
        .values("event__id", "event__titulo")
        .annotate(total=Count("id"))
        .order_by("-total", "event__titulo")
    )

    # Extrair labels e valores para o gráfico
    eventos_labels = [row["event__titulo"] for row in favoritos_qs[:12]]
    eventos_values = [row["total"] for row in favoritos_qs[:12]]

    # Top event para o card de destaque
    top_event = eventos_labels[0] if eventos_labels else "—"

    # Passe Fácil: total de usos (validações válidas) no período selecionado
    passe_uses = ValidacaoQRCode.objects.filter(
        data_validacao__gte=start_dt,
        valido=True,
    ).count()

    # Dados de gráficos (exemplos funcionais; substitua quando tiver dados reais)
    if not eventos_labels:
        # Fallback amistoso quando não há dados
        eventos_labels = ["Sem dados"]
        eventos_values = [0]

    context = {
        "summary": {
            "total_users": total_users,
            "active_today": active_today,
            "top_event": top_event,
            "passe_uses": passe_uses,
        },
        "period": period,
        "period_label": period_label,
        "eventos_labels": eventos_labels,
        "eventos_values": eventos_values,
    }

    return render(request, 'admin_personalizado/dashboard/dashboard.html', context)

@staff_member_required
@login_required
def passefacil_admin(request):
    """View para o painel administrativo do Passe Fácil"""
    # Últimas 10 validações
    validacoes_recentes = ValidacaoQRCode.objects.select_related(
        'passe_facil__user'
    ).order_by('-data_validacao')[:10]
    
    # Lista todos os passes com campos da última validação (corrigindo Subquery não correlacionada no Prefetch)
    last_val_qs = ValidacaoQRCode.objects.filter(
        passe_facil_id=OuterRef('pk')
    ).order_by('-data_validacao')

    passes = (
        PasseFacil.objects
        .select_related('user')
        .annotate(
            last_validacao_data=Subquery(last_val_qs.values('data_validacao')[:1]),
            last_validacao_valido=Subquery(last_val_qs.values('valido')[:1]),
        )
        .order_by('user__first_name', 'user__last_name')
    )
    
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
    
    # Total de usuários com Passe Fácil ativo
    total_usuarios = PasseFacil.objects.filter(ativo=True).count()
    
    # Filtro de período (all | 7d | 30d) para o gráfico
    period = request.GET.get('period', '7d')
    if period == 'all':
        # Desde sempre: do primeiro registro até hoje (cap em 60 dias para não estourar o gráfico)
        first = ValidacaoQRCode.objects.order_by('data_validacao').values_list('data_validacao', flat=True).first()
        if first:
            first_date = timezone.localdate(first)
            days_count = (hoje - first_date).days + 1
            days_count = max(1, min(days_count, 60))  # limite de 60 dias
        else:
            days_count = 1
        period_label = 'Desde sempre'
    elif period == '30d':
        days_count = 30
        period_label = 'Últimos 30 dias'
    else:
        days_count = 7
        period_label = 'Últimos 7 dias'

    # Janela de dias para agregação
    data_inicio = hoje - timedelta(days=days_count - 1)
    validacoes_por_dia = ValidacaoQRCode.objects.filter(
        data_validacao__date__gte=data_inicio,
        data_validacao__date__lte=hoje
    ).values('data_validacao__date').annotate(
        total=Count('id'),
        validas=Count('id', filter=Q(valido=True)),
        invalidas=Count('id', filter=Q(valido=False))
    ).order_by('data_validacao__date')
    
    # Prepara os dados para o gráfico
    dias = []
    totais = []
    validas_list = []
    invalidas_list = []
    
    for i in range(days_count):
        data = data_inicio + timedelta(days=i)
        dia_formatado = data.strftime('%d/%m')
        dias.append(dia_formatado)
        
        # Encontra os dados para este dia
        dados_dia = next((d for d in validacoes_por_dia 
                         if d['data_validacao__date'] == data), None)
        
        if dados_dia:
            totais.append(dados_dia['total'])
            validas_list.append(dados_dia['validas'])
            invalidas_list.append(dados_dia['invalidas'])
        else:
            totais.append(0)
            validas_list.append(0)
            invalidas_list.append(0)
    
    from django.core.serializers.json import DjangoJSONEncoder
    import json
    
    # Converte as listas para JSON manualmente
    context = {
        'title': 'Passe Fácil - Admin',
        'active_menu': 'passefacil_admin',
        'validacoes_recentes': validacoes_recentes,
        'passes': passes,
        'total_validacoes': total_validacoes,
        'validas': validas,
        'invalidas': invalidas,
        'total_usuarios': total_usuarios,
        'dias': json.dumps(dias, cls=DjangoJSONEncoder),
        'totais': json.dumps(totais, cls=DjangoJSONEncoder),
        'validas_list': json.dumps(validas_list, cls=DjangoJSONEncoder),
        'invalidas_list': json.dumps(invalidas_list, cls=DjangoJSONEncoder),
        'period': period,
        'period_label': period_label,
    }
    
    return render(request, 'admin_personalizado/passefacil/passefacilADM.html', context)

@staff_member_required
@require_http_methods(["GET", "POST"])
def enviar_notificacao(request):
    """
    View para envio de notificações personalizadas.
    
    GET: Exibe o formulário de envio de notificações.
    POST: Processa o formulário e cria uma nova notificação.
    
    Permissões requeridas:
    - Usuário deve ser staff (gerenciado pelo decorador staff_member_required)
    """
    ultimas_notificacoes = NotificacaoPersonalizada.objects.order_by('-data_criacao')[:10]
    
    if request.method == 'POST':
        # Processar o formulário
        titulo = request.POST.get('titulo', '').strip()
        mensagem = request.POST.get('mensagem', '').strip()
        
        # Validação básica
        erros = []
        if not titulo:
            erros.append('O título é obrigatório.')
        elif len(titulo) > 200:
            erros.append('O título não pode ter mais de 200 caracteres.')
            
        if not mensagem:
            erros.append('A mensagem é obrigatória.')
        
        if erros:
            for erro in erros:
                messages.error(request, erro)
        else:
            try:
                notificacao = NotificacaoPersonalizada.objects.create(
                    titulo=titulo,
                    mensagem=mensagem,
                    criado_por=request.user
                )
                messages.success(request, 'Notificação agendada com sucesso!')
                return redirect('admin_personalizado:enviar_notificacao')
                
            except Exception as e:
                messages.error(
                    request,
                    f'Ocorreu um erro ao salvar a notificação: {str(e)}'
                )
    
    # Se for GET ou se houver erros no POST, mostra o formulário
    context = {
        'title': 'Enviar Notificação',
        'opts': NotificacaoPersonalizada._meta,
        'has_view_permission': True,
        'has_add_permission': True,
        'has_change_permission': True,
        'has_delete_permission': True,
        'has_file_field': False,
        'has_editable_inline_admin_formsets': False,
        'ultimas_notificacoes': ultimas_notificacoes,
        'is_popup': False,
        'show_save': True,
        'show_save_as_new': False,
        'show_save_and_add_another': False,
        'show_save_and_continue': False,
        'show_close': True,
    }
    
    return render(
        request,
        'admin_personalizado/notificacao/enviar_notificacao.html',
        context
    )

@staff_member_required
@login_required
@require_http_methods(['POST'])
def enviar_notificacao_ajax(request):
    """
    View para envio de notificação via AJAX
    Retorna JSON com o resultado da operação
    """
    if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'error', 'message': 'Requisição inválida'}, status=400)
    
    mensagem = request.POST.get('mensagem', '').strip()
    
    if not mensagem:
        return JsonResponse(
            {'status': 'error', 'message': 'A mensagem não pode estar vazia'}, 
            status=400
        )
    
    try:
        User = get_user_model()
        usuarios = User.objects.filter(is_active=True)
        total_usuarios = usuarios.count()
        
        # Usa transação atômica para garantir que todas as notificações sejam criadas
        with transaction.atomic():
            notificacoes = [
                Notificacao(
                    usuario=usuario,
                    titulo='Nova notificação',
                    mensagem=mensagem,
                    tipo='info',
                    criado_por=request.user
                )
                for usuario in usuarios
            ]
            
            notificacoes_criadas = Notificacao.objects.bulk_create(notificacoes)
            
            # Atualiza o campo criado_por para todas as notificações
            Notificacao.objects.filter(
                id__in=[n.id for n in notificacoes_criadas]
            ).update(criado_por=request.user)
        
        return JsonResponse({
            'status': 'success',
            'message': f'Notificação enviada para {len(notificacoes_criadas)} usuários',
            'total_usuarios': total_usuarios
        })
        
    except Exception as e:
        return JsonResponse(
            {'status': 'error', 'message': f'Erro ao enviar notificações: {str(e)}'}, 
            status=500
        )
def editar_notificacao(request, pk):
    notificacao = get_object_or_404(NotificacaoPersonalizada, pk=pk)
    
    if request.method == 'POST':
        titulo = request.POST.get('titulo', '').strip()
        mensagem = request.POST.get('mensagem', '').strip()
        
        if not titulo or not mensagem:
            messages.error(request, 'Por favor, preencha todos os campos obrigatórios.')
        else:
            notificacao.titulo = titulo
            notificacao.mensagem = mensagem
            notificacao.save()
            messages.success(request, 'Notificação atualizada com sucesso!')
            return redirect('admin_personalizado:enviar_notificacao')
    
    context = {
        'notificacao': notificacao,
        'title': 'Editar Notificação'
    }
    return render(request, 'admin_personalizado/notificacao/editar_notificacao.html', context)

@staff_member_required
@login_required
@require_http_methods(['POST'])
def excluir_notificacao(request, pk):
    notificacao = get_object_or_404(NotificacaoPersonalizada, pk=pk)
    notificacao.delete()
    messages.success(request, 'Notificação excluída com sucesso!')
    return redirect('admin_personalizado:enviar_notificacao')
    