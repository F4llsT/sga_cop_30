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

    # Dados para o gráfico (exemplo: eventos por dia)
    eventos_por_dia = (
        Event.objects.filter(created_at__gte=start_dt)
        .annotate(date=TruncDate('created_at'))
        .values('date')
        .annotate(total=Count('id'))
        .order_by('date')
    )

    # Preparar dados para o gráfico
    if eventos_por_dia:
        eventos_labels = [e['date'].strftime('%d/%m') for e in eventos_por_dia]
        eventos_values = [e['total'] for e in eventos_por_dia]
    else:
        # Fallback amistoso quando não há dados
        eventos_labels = ["Sem dados"]
        eventos_values = [0]

    context = {
        "summary": {
            "total_users": total_users,
            "active_today": active_today,
            "total_events": Event.objects.count(),
            "passe_uses": passe_uses,
        },
        "period": period,
        "period_label": period_label,
        "eventos_labels": eventos_labels,
        "eventos_values": eventos_values,
        "eventos_recentes": eventos_recentes,
    }

    return render(request, 'admin_personalizado/dashboard/dashboard.html', context)

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

@gerente_required
@require_http_methods(['POST'])
def enviar_notificacao_ajax(request):
    """
    View para envio de notificação via AJAX
    Retorna JSON com o resultado da operação
    
    Permissões requeridas:
    - Acesso restrito a gerentes e superusuários
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
        
        # Processar palestrantes (array de IDs para string separada por vírgulas)
        palestrantes = data.get('palestrantes', [])
        if isinstance(palestrantes, list):
            palestrantes = ','.join(str(p) for p in palestrantes)
        
        # Criar o evento
        evento = Event.objects.create(
            titulo=data.get('titulo', ''),
            descricao=data.get('descricao', ''),
            local=data.get('local', ''),
            start_time=start_time,
            end_time=end_time,
            tags=data.get('tags', ''),
            palestrantes=palestrantes,
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
            'palestrantes': evento.palestrantes,
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
from datetime import datetime, timedelta
import json

@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_eventos(request):
    """
    API para listar (GET) e criar (POST) eventos.
    """
    if request.method == 'GET':
        try:
            eventos = Event.objects.all().order_by('start_time')
            
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
            page_obj = paginator.get_page(page)
            
            # Converter para dicionário
            eventos_list = [{
                'id': evento.id,
                'titulo': evento.titulo,
                'descricao': evento.descricao or '',
                'local': evento.local or '',
                'palestrante': evento.palestrante or '',  # Adicionado campo palestrante
                'start_time': evento.start_time.isoformat() if evento.start_time else None,
                'end_time': evento.end_time.isoformat() if evento.end_time else None,
                'tema': evento.tags or 'sustentabilidade',
                'importante': evento.importante if hasattr(evento, 'importante') else False,
                'created_at': evento.created_at.isoformat() if evento.created_at else None
            } for evento in page_obj]
            
            return JsonResponse({
                'count': paginator.count,
                'num_pages': paginator.num_pages,
                'current_page': page,
                'results': eventos_list
            }, safe=False)
        
        except Exception as e:
            return JsonResponse({
                'error': str(e),
                'detail': 'Erro ao buscar eventos'
            }, status=500)
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Validação dos dados
            required_fields = ['titulo', 'start_time', 'end_time', 'local']
            for field in required_fields:
                if field not in data or not data[field]:
                    return JsonResponse(
                        {'error': f'O campo {field} é obrigatório'}, 
                        status=400
                    )
            
            # Criação do evento
            evento = Event(
                titulo=data['titulo'],
                descricao=data.get('descricao', ''),
                local=data['local'],
                palestrante=data.get('palestrante', ''),  # Campo adicionado
                start_time=data['start_time'],
                end_time=data['end_time'],
                tags=data.get('tema', 'sustentabilidade'),
                importante=data.get('importante', False),
                created_by=request.user
            )
            
            # Validação do modelo
            evento.full_clean()
            evento.save()
            
            return JsonResponse({
                'id': evento.id,
                'message': 'Evento criado com sucesso!'
            }, status=201)
            
        except json.JSONDecodeError:
            return JsonResponse(
                {'error': 'Dados JSON inválidos'}, 
                status=400
            )
        except ValidationError as e:
            return JsonResponse(
                {'error': 'Dados inválidos', 'details': str(e.messages)},
                status=400
            )
        except Exception as e:
            return JsonResponse(
                {'error': str(e), 'detail': 'Erro ao criar evento'},
                status=500
            )

@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def api_evento_detalhe(request, evento_id):
    """
    Retorna, atualiza ou remove um evento específico.
    """
    try:
        evento = Event.objects.get(id=evento_id)
        
        if request.method == 'GET':
            return JsonResponse({
                'id': evento.id,
                'titulo': evento.titulo,
                'descricao': evento.descricao or '',
                'local': evento.local or '',
                'palestrante': evento.palestrante or '',  # Campo adicionado
                'start_time': evento.start_time.isoformat() if evento.start_time else None,
                'end_time': evento.end_time.isoformat() if evento.end_time else None,
                'tema': evento.tags or 'sustentabilidade',
                'importante': evento.importante if hasattr(evento, 'importante') else False,
                'created_at': evento.created_at.isoformat() if evento.created_at else None
            })
            
        elif request.method == 'PUT':
            try:
                data = json.loads(request.body)
                
                # Atualiza os campos fornecidos
                fields = ['titulo', 'descricao', 'local', 'palestrante', 'start_time', 'end_time', 'tema', 'importante']
                for field in fields:
                    if field in data:
                        if field == 'tema':
                            setattr(evento, 'tags', data[field])
                        else:
                            setattr(evento, field, data[field])
                
                # Validação do modelo
                evento.full_clean()
                evento.save()
                
                return JsonResponse({
                    'id': evento.id,
                    'message': 'Evento atualizado com sucesso!'
                })
                
            except json.JSONDecodeError:
                return JsonResponse(
                    {'error': 'Dados JSON inválidos'}, 
                    status=400
                )
            except ValidationError as e:
                return JsonResponse(
                    {'error': 'Dados inválidos', 'details': str(e.messages)},
                    status=400
                )
            except Exception as e:
                return JsonResponse(
                    {'error': str(e), 'detail': 'Erro ao atualizar evento'},
                    status=500
                )
                
        elif request.method == 'DELETE':
            evento.delete()
            return JsonResponse(
                {'message': 'Evento removido com sucesso!'},
                status=204
            )
            
    except Event.DoesNotExist:
        return JsonResponse(
            {'error': 'Evento não encontrado'}, 
            status=404
        )
    except Exception as e:
        return JsonResponse(
            {'error': str(e), 'detail': 'Erro ao processar a requisição'},
            status=500
        )