from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Count, Q, OuterRef, Subquery, Prefetch
from django.http import JsonResponse, Http404, HttpResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.db import transaction
from django.core.serializers.json import DjangoJSONEncoder
from datetime import timedelta, datetime, date
import json
from apps.notificacoes.models import Aviso
from apps.passefacil.models import PasseFacil, ValidacaoQRCode
from apps.agenda.models import Event
from apps.notificacoes.models import Notificacao
from .models import NotificacaoPersonalizada
from .decorators import gerente_required, superuser_required, eventos_required, staff_required

@staff_required
@eventos_required
def eventos_admin(request):
    """
    Painel administrativo de eventos.
    
    Permissões:
    - Acesso restrito a usuários de eventos, gerentes e superusuários
    """
    hoje = timezone.now().date()
    
    # Filtros
    filtro_status = request.GET.get('status', 'todos')
    filtro_data_inicio = request.GET.get('data_inicio')
    filtro_data_fim = request.GET.get('data_fim')
    
    # Query base
    eventos = Event.objects.all().order_by('start_time')
    
    # Aplicar filtros
    if filtro_status != 'todos':
        if filtro_status == 'passados':
            eventos = eventos.filter(end_time__lt=timezone.now())
        elif filtro_status == 'ativos':
            eventos = eventos.filter(
                start_time__lte=timezone.now(),
                end_time__gte=timezone.now()
            )
        elif filtro_status == 'futuros':
            eventos = eventos.filter(start_time__gt=timezone.now())
    
    # Filtros de data
    if filtro_data_inicio:
        try:
            data_inicio = filtro_data_inicio
            if not isinstance(data_inicio, date):
                from datetime import datetime
                data_inicio = datetime.strptime(filtro_data_inicio, '%Y-%m-%d').date()
            eventos = eventos.filter(start_time__date__gte=data_inicio)
        except (ValueError, TypeError):
            pass
    
    if filtro_data_fim:
        try:
            data_fim = filtro_data_fim
            if not isinstance(data_fim, date):
                from datetime import datetime
                data_fim = datetime.strptime(filtro_data_fim, '%Y-%m-%d').date()
            eventos = eventos.filter(end_time__date__lte=data_fim)
        except (ValueError, TypeError):
            pass
    
    # Contadores para os cards
    total_eventos = eventos.count()
    eventos_ativos = eventos.filter(
        start_time__lte=timezone.now(),
        end_time__gte=timezone.now()
    ).count()
    
    # Próximos eventos (próximos 7 dias)
    proxima_semana = timezone.now() + timedelta(days=7)
    proximos_eventos = eventos.filter(
        start_time__gte=timezone.now(),
        start_time__lte=proxima_semana
    ).order_by('start_time')[:5]
    
    # Eventos mais populares (com mais favoritos)
    eventos_populares = eventos.order_by('-created_at')[:5]
    
    context = {
        'eventos': eventos,
        'total_eventos': total_eventos,
        'eventos_ativos': eventos_ativos,
        'proximos_eventos': proximos_eventos,
        'eventos_populares': eventos_populares,
        'filtro_status': filtro_status,
        'filtro_data_inicio': filtro_data_inicio or '',
        'filtro_data_fim': filtro_data_fim or '',
        'hoje': hoje.strftime('%Y-%m-%d'),
    }
    
    return render(request, 'admin_personalizado/evento/eventos.html', context)

from django.db.models import Count
from django.db.models.functions import TruncDate
from apps.agenda.models import Event
from apps.passefacil.models import ValidacaoQRCode

@staff_required
def dashboard(request):
    """
    Dashboard administrativo do sistema.
    
    Permissões:
    - Acesso restrito a usuários staff (gerentes e superusuários)
    """
    User = get_user_model()

    # Métricas básicas
    total_users = User.objects.count()
    today = timezone.localdate()
    active_today = User.objects.filter(last_login__date=today).count()

    # Filtro de período (apenas para os eventos)
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

    # Eventos mais recentes
    eventos_recentes = Event.objects.filter(
        created_at__gte=start_dt
    ).order_by('-created_at')[:5]

    # Passe Fácil: total de usos (validações válidas) no período selecionado
    passe_uses = ValidacaoQRCode.objects.filter(
        data_validacao__gte=start_dt,
        valido=True,
    ).count()

    # Eventos com número de favoritos (apenas eventos com pelo menos 1 favorito)
    eventos_com_favoritos = (
        Event.objects.annotate(
            num_favoritos=Count('agenda_usuarios')
        )
        .filter(num_favoritos__gt=0)
        .order_by('-num_favoritos')[:10]  # Top 10 eventos favoritados
    )

    # Encontrar o evento mais favoritado
    top_event_obj = eventos_com_favoritos.first() if eventos_com_favoritos else None
    top_event = top_event_obj.titulo if top_event_obj else "Nenhum"

    # Dados para o gráfico (eventos mais favoritados)
    if eventos_com_favoritos:
        eventos_labels = [e.titulo[:30] + '...' if len(e.titulo) > 30 else e.titulo for e in eventos_com_favoritos]
        eventos_values = [e.num_favoritos for e in eventos_com_favoritos]
    else:
        # Fallback amistoso quando não há dados
        eventos_labels = ["Nenhum evento favoritado"]
        eventos_values = [0]

    context = {
        "summary": {
            "total_users": total_users,
            "active_today": active_today,
            "total_events": Event.objects.count(),
            "passe_uses": passe_uses,
            "top_event": top_event,
        },
        "period": period,
        "period_label": period_label,
        "eventos_labels": eventos_labels,
        "eventos_values": eventos_values,
        "eventos_recentes": eventos_recentes,
        "eventos_com_favoritos": eventos_com_favoritos,
    }

    return render(request, 'admin_personalizado/dashboard/dashboard.html', context)

@staff_required
def criar_favoritos_teste(request):
    """
    View temporária para criar favoritos de teste
    """
    from apps.agenda.models import Event, UserAgenda
    from django.contrib.auth import get_user_model
    import random
    
    User = get_user_model()
    
    # Pega eventos e usuários
    eventos = list(Event.objects.all()[:5])  # Primeiros 5 eventos
    usuarios = list(User.objects.filter(is_active=True)[:5])  # Primeiros 5 usuários
    
    if eventos and usuarios:
        criados = 0
        for evento in eventos:
            # Adiciona de 1 a 5 favoritos aleatórios para cada evento
            num_favoritos = random.randint(1, min(5, len(usuarios)))
            usuarios_selecionados = random.sample(usuarios, num_favoritos)
            
            for usuario in usuarios_selecionados:
                if not UserAgenda.objects.filter(user=usuario, event=evento).exists():
                    UserAgenda.objects.create(user=usuario, event=evento)
                    criados += 1
        
        messages.success(request, f'Foram criados {criados} favoritos de teste!')
    else:
        messages.error(request, 'Não há eventos ou usuários suficientes para criar favoritos.')
    
    return redirect('admin_personalizado:dashboard')

@gerente_required
def passefacil_admin(request):
    """
    Painel administrativo do Passe Fácil.
    
    Permissões:
    - Acesso restrito a gerentes e superusuários
    """
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

@gerente_required
@require_http_methods(["GET", "POST"])
def enviar_notificacao(request):
    """
    View para envio de notificações personalizadas.
    
    GET: Exibe o formulário de envio de notificações.
    POST: Processa o formulário e cria uma nova notificação.
    
    Permissões requeridas:
    - Acesso restrito a gerentes e superusuários
    """
    from apps.notificacoes.models import Notificacao, NotificacaoUsuario
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    # Remove o limitador para que o DataTables faça a paginação corretamente
    ultimas_notificacoes = Notificacao.objects.order_by('-criada_em')
    
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
                # Obter o tipo da notificação do formulário
                tipo = request.POST.get('tipo', 'info')
                
                # Obter todos os usuários ativos
                usuarios = User.objects.filter(is_active=True)
                
                # Criar uma única notificação
                notificacao = Notificacao.objects.create(
                    titulo=titulo,
                    mensagem=mensagem,
                    tipo=tipo,
                    criado_por=request.user
                )
                
                # Adicionar todos os usuários ativos à notificação
                notificacao.adicionar_usuarios(usuarios)
                
                messages.success(request, f'Notificação criada com sucesso para {usuarios.count()} usuários ativos!')
                return redirect('admin_personalizado:enviar_notificacao')
                
            except Exception as e:
                messages.error(
                    request,
                    f'Ocorreu um erro ao salvar a notificação: {str(e)}'
                )
    
    # Se for GET ou se houver erros no POST, mostra o formulário
    context = {
        'title': 'Enviar Notificação',
        'opts': Notificacao._meta,
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
        'total_usuarios': User.objects.filter(is_active=True).count(),
    }
    
    return render(
        request,
        'admin_personalizado/notificacao/enviar_notificacao.html',
        context
    )

@gerente_required
@require_http_methods(['POST'])
def enviar_notificacao_ajax(request):
    """
    View para envio de notificação via AJAX
    Retorna JSON com o resultado da operação
    
    Permissões requeridas:
    - Acesso restrito a gerentes e superusuários
    """
    from apps.notificacoes.models import Notificacao, NotificacaoUsuario
    
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
        
        # Obtém o tipo da notificação do formulário
        tipo = request.POST.get('tipo', 'info')
        
        # Usa transação atômica para garantir que todas as notificações sejam criadas
        with transaction.atomic():
            # Cria uma única notificação
            notificacao = Notificacao.objects.create(
                titulo='Nova notificação',
                mensagem=mensagem,
                tipo=tipo,
                criado_por=request.user
            )
            
            # Adiciona todos os usuários ativos à notificação
            notificacao.adicionar_usuarios(usuarios)
        
        return JsonResponse({
            'status': 'success',
            'message': f'Notificação criada para {total_usuarios} usuários ativos',
            'total_usuarios': total_usuarios,
            'notificacao_id': notificacao.id
        })
        
    except Exception as e:
        return JsonResponse(
            {'status': 'error', 'message': f'Erro ao enviar notificações: {str(e)}'}, 
            status=500
        )

@gerente_required
def editar_notificacao(request, pk):
    """
    Edita uma notificação existente.
    
    Permissões requeridas:
    - Acesso restrito a gerentes e superusuários
    """
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

@gerente_required
@require_http_methods(['POST'])
def excluir_notificacao(request, pk):
    """
    Exclui uma notificação existente.
    
    Permissões requeridas:
    - Acesso restrito a gerentes e superusuários
    """
    notificacao = get_object_or_404(NotificacaoPersonalizada, pk=pk)
    notificacao.delete()
    messages.success(request, 'Notificação excluída com sucesso!')
    return redirect('admin_personalizado:enviar_notificacao')


@staff_required
@eventos_required
@require_http_methods(['POST'])
def criar_evento(request):
    """
    Cria um novo evento.
    """
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST.dict()
        
        # Processar datas
        data_inicio_str = f"{data.get('data_inicio')} {data.get('hora_inicio', '00:00')}"
        data_fim_str = f"{data.get('data_fim')} {data.get('hora_fim', '23:59')}"
        
        try:
            start_time = timezone.make_aware(
                datetime.strptime(data_inicio_str, '%Y-%m-%d %H:%M')
            )
            end_time = timezone.make_aware(
                datetime.strptime(data_fim_str, '%Y-%m-%d %H:%M')
            )
        except (ValueError, TypeError) as e:
            return JsonResponse({
                'error': 'Formato de data/hora inválido',
                'detail': str(e)
            }, status=400)
        
        # Processar palestrante
        palestrante = data.get('palestrante', data.get('palestrantes', ''))
        if isinstance(palestrante, list):
            palestrante = ', '.join(str(p) for p in palestrante)
        
        # Criar o evento
        evento = Event.objects.create(
            titulo=data.get('titulo', ''),
            descricao=data.get('descricao', ''),
            local=data.get('local', ''),
            start_time=start_time,
            end_time=end_time,
            tags=data.get('tags', ''),
            palestrante=palestrante,
            latitude=float(data.get('latitude')) if data.get('latitude') else None,
            longitude=float(data.get('longitude')) if data.get('longitude') else None
        )
        
        return JsonResponse({
            'id': evento.id,
            'titulo': evento.titulo,
            'descricao': evento.descricao,
            'local': evento.local,
            'start_time': evento.start_time.isoformat(),
            'end_time': evento.end_time.isoformat(),
            'tags': evento.tags,
            'palestrante': evento.palestrante,
            'latitude': evento.latitude,
            'longitude': evento.longitude
        }, status=201)
        
    except Exception as e:
        return JsonResponse({
            'error': 'Erro ao criar evento',
            'detail': str(e)
        }, status=400)

@staff_required
@eventos_required
@require_http_methods(['GET', 'PUT', 'DELETE'])
def editar_evento(request, evento_id):
    """
    Gerencia um evento existente.
    
    Métodos suportados:
    - GET: Retorna os dados do evento em formato JSON
    - PUT: Atualiza o evento com os dados fornecidos
    - DELETE: Remove o evento
    """
    evento = get_object_or_404(Event, id=evento_id)
    
    if request.method == 'GET':
        return JsonResponse({
            'id': evento.id,
            'titulo': evento.titulo,
            'descricao': evento.descricao,
            'local': evento.local,
            'start_time': evento.start_time.isoformat() if evento.start_time else None,
            'end_time': evento.end_time.isoformat() if evento.end_time else None,
            'tema': evento.tags or 'sustentabilidade',
            'importante': evento.importante if hasattr(evento, 'importante') else False
        })
    
    elif request.method == 'PUT':
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST.dict()
            
            # Atualizar campos básicos
            evento.titulo = data.get('titulo', evento.titulo)
            evento.descricao = data.get('descricao', evento.descricao)
            evento.local = data.get('local', evento.local)
            evento.tags = data.get('tema', evento.tags)
            
            if 'importante' in data:
                evento.importante = data['importante']
            
            # Atualizar datas se fornecidas
            if data.get('start_time'):
                evento.start_time = timezone.make_aware(
                    datetime.fromisoformat(data['start_time'])
                )
            
            if data.get('end_time'):
                evento.end_time = timezone.make_aware(
                    datetime.fromisoformat(data['end_time'])
                )
            
            evento.save()
            
            return JsonResponse({
                'id': evento.id,
                'titulo': evento.titulo,
                'descricao': evento.descricao,
                'local': evento.local,
                'start_time': evento.start_time.isoformat() if evento.start_time else None,
                'end_time': evento.end_time.isoformat() if evento.end_time else None,
                'tema': evento.tags or 'sustentabilidade',
                'importante': evento.importante if hasattr(evento, 'importante') else False
            })
            
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'detail': 'Erro ao atualizar o evento'
            }, status=400)
    
    elif request.method == 'DELETE':
        try:
            evento_id = evento.id
            evento.delete()
            return JsonResponse({
                'success': True,
                'message': f'Evento {evento_id} excluído com sucesso!'
            })
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'detail': 'Erro ao excluir o evento'
            }, status=400)
    
    return JsonResponse({
        'error': 'Método não permitido',
        'allowed_methods': ['GET', 'PUT', 'DELETE']
    }, status=405)













from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Q
from django.urls import reverse
from datetime import datetime, timedelta
import json

@login_required
@staff_required
@require_http_methods(["POST"])
def excluir_evento(request, evento_id):
    """
    Exclui um evento existente.
    """
    try:
        evento = get_object_or_404(Event, id=evento_id)
        
        # Verificar permissões
        if not request.user.is_superuser and hasattr(evento, 'created_by') and evento.created_by != request.user:
            messages.error(request, 'Você não tem permissão para excluir este evento.')
            return redirect('admin_personalizado:eventos_admin')
        
        titulo_evento = evento.titulo
        evento.delete()
        
        messages.success(request, f'Evento "{titulo_evento}" excluído com sucesso!')
        return redirect('admin_personalizado:eventos_admin')
        
    except Exception as e:
        messages.error(request, f'Erro ao excluir o evento: {str(e)}')
        return redirect('admin_personalizado:eventos_admin')

@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_eventos(request):
    """
    API para listar (GET) e criar (POST) eventos.
    """
    from apps.agenda.serializers import EventSerializer
    from django.core.exceptions import ValidationError
    from django.core.paginator import Paginator, EmptyPage
    
    if request.method == 'GET':
        try:
            # Usa todos os eventos (sem filtro do manager)
            eventos = Event.all_objects.all().order_by('start_time')
            
            # Aplicar filtros
            search = request.GET.get('search')
            if search:
                eventos = eventos.filter(
                    Q(titulo__icontains=search) |
                    Q(descricao__icontains=search) |
                    Q(local__icontains=search) |
                    Q(palestrante__icontains=search)
                )
            
            start_date = request.GET.get('start_date')
            if start_date:
                try:
                    start_date = timezone.make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
                    eventos = eventos.filter(start_time__gte=start_date)
                except ValueError:
                    pass
            
            end_date = request.GET.get('end_date')
            if end_date:
                try:
                    end_date = timezone.make_aware(datetime.strptime(end_date, '%Y-%m-%d')) + timedelta(days=1)
                    eventos = eventos.filter(start_time__lte=end_date)
                except ValueError:
                    pass
            
            importante = request.GET.get('importante')
            if importante and importante.lower() == 'true':
                eventos = eventos.filter(importante=True)
            
            # Paginação
            page = int(request.GET.get('page', 1))
            per_page = int(request.GET.get('per_page', 10))
            paginator = Paginator(eventos, per_page)
            
            try:
                page_obj = paginator.get_page(page)
            except EmptyPage:
                return JsonResponse({
                    'count': paginator.count,
                    'num_pages': paginator.num_pages,
                    'current_page': page,
                    'results': []
                }, safe=False)
            
            # Usar o serializador para formatar os dados
            serializer = EventSerializer(page_obj, many=True)
            
            return JsonResponse({
                'count': paginator.count,
                'num_pages': paginator.num_pages,
                'current_page': page,
                'results': serializer.data
            }, safe=False)
        
        except Exception as e:
            print("Erro ao buscar eventos:", str(e))
            return JsonResponse({
                'error': str(e),
                'detail': 'Erro ao buscar eventos'
            }, status=500)
    
    elif request.method == 'POST':
        try:
            # Log dos dados brutos recebidos
            print("Dados brutos recebidos:", request.body)
            
            try:
                data = json.loads(request.body)
                print("Dados decodificados:", data)
            except json.JSONDecodeError as je:
                print("Erro ao decodificar JSON:", str(je))
                return JsonResponse(
                    {'error': 'Dados JSON inválidos', 'detail': str(je)}, 
                    status=400
                )
            
            # Adiciona o usuário atual como criador do evento
            data['created_by'] = request.user.id
            
            # Log dos campos obrigatórios
            required_fields = ['titulo', 'start_time', 'end_time', 'local']
            missing_fields = [field for field in required_fields if field not in data or not data[field]]
            
            if missing_fields:
                error_msg = f'Campos obrigatórios faltando: {", ".join(missing_fields)}'
                print("Erro de validação:", error_msg)
                return JsonResponse({
                    'error': 'Dados inválidos',
                    'details': {'required_fields': error_msg}
                }, status=400)
            
            # Log dos dados antes da validação
            print("Dados antes da validação:", data)
            
            # Usa o serializador para validar e salvar
            serializer = EventSerializer(data=data)
            
            if serializer.is_valid():
                try:
                    evento = serializer.save()
                    print("Evento criado com sucesso:", evento.id)
                    return JsonResponse({
                        'id': evento.id,
                        'message': 'Evento criado com sucesso!',
                        'data': EventSerializer(evento).data
                    }, status=201)
                except Exception as save_error:
                    print("Erro ao salvar o evento:", str(save_error))
                    return JsonResponse({
                        'error': 'Erro ao salvar o evento',
                        'details': str(save_error)
                    }, status=500)
            else:
                print("Erros de validação:", serializer.errors)
                return JsonResponse({
                    'error': 'Dados inválidos',
                    'details': serializer.errors
                }, status=400)
                
        except Exception as e:
            import traceback
            print("Erro inesperado:", str(e))
            print("Traceback:", traceback.format_exc())
            return JsonResponse(
                {'error': 'Erro interno do servidor', 'detail': str(e)},
                status=500
            )

@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def api_evento_detalhe(request, evento_id):
    """
    Retorna, atualiza ou remove um evento específico.
    """
    evento = get_object_or_404(Event, id=evento_id)
    
    # API de detalhe de evento: GET/PUT/DELETE
    if request.method == 'GET':
        return JsonResponse({
            'success': True,
            'evento': {
                'id': evento.id,
                'titulo': evento.titulo,
                'descricao': evento.descricao,
                'local': evento.local,
                'start_time': evento.start_time.isoformat() if evento.start_time else None,
                'end_time': evento.end_time.isoformat() if evento.end_time else None,
                'tags': getattr(evento, 'tags', None),
                'importante': bool(getattr(evento, 'importante', False)),
                'latitude': getattr(evento, 'latitude', None),
                'longitude': getattr(evento, 'longitude', None),
                'palestrante': getattr(evento, 'palestrante', '')
            }
        })
    
    if request.method == 'PUT':
        try:
            data = json.loads(request.body or '{}')
        except json.JSONDecodeError:
            return JsonResponse({'detail': 'JSON inválido'}, status=400)
        from apps.agenda.serializers import EventSerializer
        serializer = EventSerializer(evento, data=data, partial=True)
        if serializer.is_valid():
            evento = serializer.save()
            return JsonResponse(serializer.data, safe=False)
        return JsonResponse({'detail': 'Dados inválidos', 'errors': serializer.errors}, status=400)
    
    if request.method == 'DELETE':
        eid = evento.id
        evento.delete()
        return JsonResponse({'success': True, 'message': f'Evento {eid} excluído com sucesso!'})
    
    return JsonResponse({'error': 'Método não permitido', 'allowed_methods': ['GET', 'PUT', 'DELETE']}, status=405)


@staff_required
def avisos_admin(request):
    """
    Painel administrativo de avisos importantes.
    GET: renderiza a página com avisos ativos e histórico
    POST: cria um novo aviso (form padrão)
    """
    if request.method == 'POST':
        try:
            titulo = request.POST.get('titulo')
            mensagem = request.POST.get('mensagem')
            importancia = request.POST.get('importancia', 'info')
            data_expiracao = request.POST.get('data_expiracao')
            horario_expiracao = request.POST.get('horario_expiracao')
            fixo = request.POST.get('fixo') == 'on'
            ativo = request.POST.get('ativo') == 'on'

            expiracao = None
            if data_expiracao:
                if horario_expiracao:
                    expiracao = timezone.make_aware(
                        datetime.strptime(f"{data_expiracao} {horario_expiracao}", '%Y-%m-%d %H:%M')
                    )
                else:
                    expiracao = timezone.make_aware(
                        datetime.strptime(f"{data_expiracao} 23:59", '%Y-%m-%d %H:%M')
                    )

            aviso = Aviso.objects.create(
                titulo=titulo,
                mensagem=mensagem,
                importancia=importancia,
                data_expiracao=expiracao,
                fixo_no_topo=fixo,
                ativo=ativo,
                criado_por=request.user
            )

            messages.success(request, 'Aviso publicado com sucesso!')
            return redirect('admin_personalizado:avisos_admin')
        except Exception as e:
            messages.error(request, f'Erro ao criar aviso: {str(e)}')
            return redirect('admin_personalizado:avisos_admin')

    avisos_ativos = Aviso.objects.filter(ativo=True).exclude(
        data_expiracao__lt=timezone.now()
    ).order_by('-fixo_no_topo', '-data_criacao')

    avisos_historico = Aviso.objects.filter(
        Q(ativo=False) | Q(data_expiracao__lt=timezone.now())
    ).order_by('-data_criacao')[:20]

    context = {
        'avisos_ativos': avisos_ativos,
        'avisos_historico': avisos_historico,
    }

    return render(request, 'admin_personalizado/avisos/gerenciar_avisos.html', context)


@require_http_methods(["POST", "DELETE"])
@login_required
@staff_required
def excluir_aviso(request, aviso_id):
    """
    Move um aviso para o histórico (desativa).
    """
    try:
        aviso = get_object_or_404(Aviso, id=aviso_id)
        aviso.ativo = False
        aviso.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Aviso movido para o histórico com sucesso!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao mover aviso para o histórico: {str(e)}'
        }, status=500)

@staff_required
@require_http_methods(["GET", "POST"])
def avisos_api(request):
    """
    API para gerenciar avisos (GET, POST).
    """
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse(
            {'success': False, 'message': 'Acesso não autorizado'}, 
            status=403
        )

    if request.method == 'GET':
        # Get active and historical notices
        avisos_ativos = Aviso.objects.filter(
            Q(ativo=True) & 
            (Q(data_expiracao__isnull=True) | Q(data_expiracao__gte=timezone.now()))
        ).order_by('-data_criacao')

        historico_avisos = Aviso.objects.filter(
            Q(ativo=False) | 
            (Q(data_expiracao__isnull=False) & Q(data_expiracao__lt=timezone.now()))
        ).order_by('-data_expiracao')

        def serialize_aviso(aviso):
            return {
                'id': aviso.id,
                'titulo': aviso.titulo,
                'mensagem': aviso.mensagem,
                'nivel': aviso.nivel,
                'data_criacao': aviso.data_criacao,
                'data_expiracao': aviso.data_expiracao,
                'fixo_no_topo': aviso.fixo_no_topo,
                'ativo': aviso.ativo,
                'criado_por': aviso.criado_por.get_full_name() or aviso.criado_por.username
            }

        return JsonResponse({
            'success': True,
            'avisos_ativos': [serialize_aviso(aviso) for aviso in avisos_ativos],
            'avisos_historico': [serialize_aviso(aviso) for aviso in historico_avisos]
        })
    
    elif request.method == 'POST':
        try:
            # Handle both JSON and form-data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST.dict()
                # Convert empty strings to None for optional fields
                for key in ['data_expiracao', 'horario_expiracao']:
                    if key in data and not data[key]:
                        data[key] = None

            # Combine date and time if both are provided
            data_expiracao = None
            if data.get('data_expiracao') and data.get('horario_expiracao'):
                data_expiracao = timezone.make_aware(
                    datetime.strptime(
                        f"{data['data_expiracao']} {data['horario_expiracao']}",
                        '%Y-%m-%d %H:%M'
                    )
                )
            elif data.get('data_expiracao'):
                data_expiracao = timezone.make_aware(
                    datetime.strptime(data['data_expiracao'], '%Y-%m-%d')
                )

            # Create the notice
            aviso = Aviso.objects.create(
                titulo=data['titulo'],
                mensagem=data['mensagem'],
                nivel=data.get('nivel', 'info'),
                data_expiracao=data_expiracao,
                fixo_no_topo=data.get('fixo_no_topo') == 'on',
                ativo=data.get('ativo', True) != 'false',  # Handle both string 'false' and boolean false
                criado_por=request.user
            )

            return JsonResponse({
                'success': True,
                'message': 'Aviso criado com sucesso!',
                'aviso': {
                    'id': aviso.id,
                    'titulo': aviso.titulo,
                    'mensagem': aviso.mensagem,
                    'nivel': aviso.nivel,
                    'data_expiracao': aviso.data_expiracao.isoformat() if aviso.data_expiracao else None,
                    'fixo_no_topo': aviso.fixo_no_topo,
                    'ativo': aviso.ativo
                }
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse(
                {'success': False, 'message': 'Erro ao processar os dados do formulário'},
                status=400
            )
        except Exception as e:
            return JsonResponse(
                {'success': False, 'message': f'Erro ao salvar o aviso: {str(e)}'},
                status=500
            )

    return JsonResponse(
        {'success': False, 'message': 'Método não permitido'},
        status=405
    )


@require_http_methods(["POST"])
def fixar_aviso(request, aviso_id):
    """
    Alterna o status de fixação de um aviso.
    """
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse(
            {'success': False, 'message': 'Acesso não autorizado'}, 
            status=403
        )
    
    try:
        aviso = get_object_or_404(Aviso, id=aviso_id)
        # Inverte o status de fixação
        aviso.fixo_no_topo = not aviso.fixo_no_topo
        aviso.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Status de fixação atualizado com sucesso!',
            'fixo_no_topo': aviso.fixo_no_topo
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao atualizar o status de fixação: {str(e)}'
        }, status=500)