from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model
from apps.usuarios.models import Usuario
from django.db.models import Q
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib.auth.models import Group
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
import json
from django.views.decorators.csrf import csrf_exempt
from django.db import models
from django.conf import settings

def is_superuser(user):
    """Verifica se o usuário é superusuário."""
    return user.is_superuser

def is_gerente(user):
    """Verifica se o usuário pertence ao grupo Gerente."""
    return user.groups.filter(name='Gerente').exists() or user.is_superuser

from .decorators import superuser_required, gerente_required, eventos_required, staff_required

# Modelo para registrar alterações de papel
class PapelHistorico(models.Model):
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='historico_papeis'
    )
    papel_anterior = models.CharField(max_length=50)
    novo_papel = models.CharField(max_length=50)
    alterado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='alteracoes_realizadas'
    )
    data_alteracao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-data_alteracao']
        verbose_name = 'Histórico de Papel'
        verbose_name_plural = 'Históricos de Papéis'

# No arquivo views_usuarios.py
@login_required
def detalhes_usuario(request, user_id):
    """
    Exibe os detalhes completos de um usuário.
    
    Permissões:
    - Superusuário: Pode ver e editar todos os usuários
    - Outros usuários: Podem ver e editar apenas o próprio perfil
    """
    usuario = get_object_or_404(get_user_model(), id=user_id)
    
    # Verifica se o usuário tem permissão para ver os detalhes
    if not (request.user.is_superuser or request.user == usuario):
        return HttpResponseForbidden("Você não tem permissão para acessar esta página.")
    
    # Obtém os papéis disponíveis (apenas para superusuários)
    papeis_disponiveis = []
    if request.user.is_superuser:
        papeis_disponiveis = [
            {'id': 'USUARIO', 'name': 'Usuário Comum'},
            {'id': 'EVENTOS', 'name': 'Usuário de Eventos'},
            {'id': 'GERENTE', 'name': 'Usuário Gerente'},
            {'id': 'SUPERUSER', 'name': 'Superusuário'}
        ]
    
    # Obtém o histórico de alterações de papel (apenas para superusuários)
    historico_papeis = []
    if request.user.is_superuser:
        historico_papeis = LogEntryManager.get_user_role_history(usuario)
    
    context = {
        'usuario': usuario,
        'papeis_disponiveis': papeis_disponiveis,
        'historico_papeis': historico_papeis,
        'agora': timezone.now(),
    }
    return render(request, 'admin_personalizado/usuarios/usuario_detalhes.html', context)

@require_http_methods(["POST"])
@gerente_required
@login_required
def alterar_papel_usuario(request, user_id):
    """
    Altera o papel de um usuário.
    
    Permissões:
    - Apenas superusuários podem atribuir papel de superusuário
    - Gerentes podem atribuir apenas papéis de Usuário Comum e Usuário de Eventos
    """
    try:
        data = json.loads(request.body)
        novo_papel_id = data.get('novo_papel')
        
        if not novo_papel_id:
            return JsonResponse(
                {'success': False, 'message': 'Nenhum papel especificado'}, 
                status=400
            )
            
        usuario = get_object_or_404(get_user_model(), id=user_id)
        
        # Impede que o usuário altere seu próprio papel
        if usuario == request.user:
            return JsonResponse({
                'success': False, 
                'message': 'Você não pode alterar seu próprio papel.'
            }, status=403)
            
        # Verifica se o usuário tem permissão para atribuir o novo papel
        if novo_papel_id == 'SUPERUSER' and not request.user.is_superuser:
            return JsonResponse({
                'success': False, 
                'message': 'Apenas superusuários podem atribuir este papel.'
            }, status=403)
            
        # Verifica se é gerente tentando atribuir papel de gerente ou superior
        if request.user.role == 'GERENTE' and novo_papel_id in ['GERENTE', 'SUPERUSER']:
            return JsonResponse({
                'success': False,
                'message': 'Você não tem permissão para atribuir este papel.'
            }, status=403)
        
        # Atualiza o papel do usuário
        with transaction.atomic():
            papel_anterior = usuario.role
            usuario.role = novo_papel_id
            
            # Configura flags de superusuário e staff conforme necessário
            if novo_papel_id == 'SUPERUSER':
                usuario.is_superuser = True
                usuario.is_staff = True
            else:
                usuario.is_superuser = False
                usuario.is_staff = (novo_papel_id == 'GERENTE')
            
            usuario.save()
            
            # Atualiza os grupos do usuário
            usuario.groups.clear()
            
            if novo_papel_id == 'GERENTE':
                grupo, _ = Group.objects.get_or_create(name='Usuário Gerente')
                usuario.groups.add(grupo)
            elif novo_papel_id == 'EVENTOS':
                grupo, _ = Group.objects.get_or_create(name='Usuário de Eventos')
                usuario.groups.add(grupo)
            
            # Registra a mudança de papel
            if papel_anterior != novo_papel_id:
                PapelHistorico.objects.create(
                    usuario=usuario,
                    papel_anterior=papel_anterior,
                    novo_papel=novo_papel_id,
                    alterado_por=request.user
                )
        
        return JsonResponse({
            'success': True, 
            'message': 'Papel do usuário atualizado com sucesso!',
            'novo_papel': usuario.get_role_display(),
            'is_superuser': usuario.is_superuser,
            'is_staff': usuario.is_staff,
            'is_active': usuario.is_active
        })
            
    except Exception as e:
        return JsonResponse(
            {'success': False, 'message': f'Erro ao alterar papel: {str(e)}'}, 
            status=500
        )

@login_required
@gerente_required
def listar_usuarios(request):
    """
    Lista todos os usuários do sistema.
    
    Permissões:
    - Superusuários: Veem todos os usuários
    - Gerentes: Veem todos os usuários, exceto superusuários
    """
    # Obtém os usuários com base nas permissões
    if request.user.is_superuser:
        usuarios = get_user_model().objects.all()
    else:
        # Gerentes veem todos os usuários, exceto superusuários
        usuarios = get_user_model().objects.filter(
            Q(role__in=['USUARIO', 'EVENTOS', 'GERENTE']) | 
            Q(pk=request.user.pk)  # Inclui o próprio gerente
        ).distinct()
    
    # Aplica filtro de busca se houver
    search_term = request.GET.get('search', '').strip()
    if search_term:
        usuarios = usuarios.filter(
            Q(first_name__icontains=search_term) |
            Q(last_name__icontains=search_term) |
            Q(email__icontains=search_term)
        )
    
    # Paginação
    page = request.GET.get('page', 1)
    paginator = Paginator(usuarios, 10)  # 10 usuários por página
    
    try:
        usuarios_paginados = paginator.page(page)
    except PageNotAnInteger:
        usuarios_paginados = paginator.page(1)
    except EmptyPage:
        usuarios_paginados = paginator.page(paginator.num_pages)
    
    context = {
        'object_list': usuarios_paginados,
        'page_obj': usuarios_paginados,
        'is_paginated': usuarios_paginados.has_other_pages(),
        'paginator': paginator,
        'agora': timezone.now(),
        # Adicionando as variáveis usadas nos cards de estatística
        'total_usuarios': usuarios.count(),
        'ativos_count': usuarios.filter(is_active=True).count(),
        'inativos_count': usuarios.filter(is_active=False).count(),
        'admins_count': usuarios.filter(is_superuser=True).count(),
    }
    
    return render(request, 'admin_personalizado/usuarios/usuario_list.html', context)

class LogEntryManager:
    @staticmethod
    def log_user_role_change(user, request_user, old_role, new_role):
        """Registra a alteração de papel do usuário no log de auditoria."""
        LogEntry.objects.log_action(
            user_id=request_user.id,
            content_type_id=ContentType.objects.get_for_model(user).pk,
            object_id=user.id,
            object_repr=str(user),
            action_flag=CHANGE,
            change_message=json.dumps({
                'event': 'ROLE_CHANGE',
                'old_role': old_role,
                'new_role': new_role,
                'timestamp': timezone.now().isoformat()
            })
        )

    @staticmethod
    def get_user_role_history(user):
        """Obtém o histórico de alterações de papel do usuário."""
        content_type = ContentType.objects.get_for_model(user)
        logs = LogEntry.objects.filter(
            content_type=content_type,
            object_id=user.id
        ).order_by('-action_time')
        
        history = []
        for log in logs:
            try:
                change_message = json.loads(log.change_message)
                if isinstance(change_message, dict) and change_message.get('event') == 'ROLE_CHANGE':
                    history.append({
                        'date': log.action_time,
                        'changed_by': log.user,
                        'old_role': change_message.get('old_role'),
                        'new_role': change_message.get('new_role')
                    })
            except (json.JSONDecodeError, AttributeError):
                continue
        
        return history

@require_http_methods(["POST"])
@gerente_required
@login_required
@user_passes_test(is_superuser)
def alterar_papel_usuario(request, user_id):
    """Altera o papel de um usuário (promover/rebaixar)."""
    User = get_user_model()
    user = get_object_or_404(User, id=user_id)
    
    # Verifica se o usuário atual tem permissão para alterar este usuário
    if not (request.user.is_superuser or (is_gerente(request.user) and not user.is_superuser)):
        return JsonResponse(
            {'success': False, 'message': 'Permissão negada.'}, 
            status=403
        )
    
    acao = request.POST.get('acao')
    old_role = 'Administrador' if user.is_superuser else \
              'Gerente' if user.groups.filter(name='Gerente').exists() else \
              'Usuário'
    
    try:
        with transaction.atomic():
            if acao == 'promover':
                if user.is_superuser:
                    return JsonResponse(
                        {'success': False, 'message': 'Este usuário já é um administrador.'}, 
                        status=400
                    )
                if user.groups.filter(name='Gerente').exists():
                    # Promover para administrador
                    user.is_superuser = True
                    user.is_staff = True
                    user.groups.clear()
                    new_role = 'Administrador'
                else:
                    # Promover para gerente
                    gerente_group = Group.objects.get(name='Gerente')
                    user.groups.add(gerente_group)
                    new_role = 'Gerente'
            
            elif acao == 'rebaixar':
                if user.is_superuser:
                    # Rebaixar para gerente
                    user.is_superuser = False
                    user.is_staff = True
                    gerente_group = Group.objects.get(name='Gerente')
                    user.groups.clear()
                    user.groups.add(gerente_group)
                    new_role = 'Gerente'
                elif user.groups.filter(name='Gerente').exists():
                    # Rebaixar para usuário
                    user.groups.clear()
                    user.is_staff = False
                    new_role = 'Usuário'
                else:
                    return JsonResponse(
                        {'success': False, 'message': 'Este usuário já é um usuário comum.'}, 
                        status=400
                    )
            
            user.save()
            
            # Registra a alteração no log
            LogEntryManager.log_user_role_change(
                user=user,
                request_user=request.user,
                old_role=old_role,
                new_role=new_role
            )
            
            return JsonResponse({
                'success': True, 
                'message': f'Papel alterado para {new_role} com sucesso!',
                'novo_papel': new_role,
                'is_active': user.is_active
            })
            
    except Exception as e:
        return JsonResponse(
            {'success': False, 'message': f'Erro ao alterar papel: {str(e)}'}, 
            status=500
        )

@require_POST
@login_required
@superuser_required
def atualizar_papel_usuario(request, user_id):
    """
    Atualiza o papel de um usuário via AJAX.
    
    Permissões:
    - Apenas superusuários podem alterar papéis de usuário
    """
    if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'message': 'Requisição inválida'}, status=400)
    
    try:
        user = get_object_or_404(get_user_model(), pk=user_id)
        novo_papel = request.POST.get('novo_papel')
        
        # Verifica se o papel é válido
        papeis_validos = dict(Usuario.Role.choices).keys()
        if novo_papel not in papeis_validos:
            return JsonResponse({
                'success': False, 
                'message': 'Papel inválido.'
            }, status=400)
        
        # Verifica se o usuário não está tentando modificar a si mesmo
        if user == request.user:
            return JsonResponse({
                'success': False, 
                'message': 'Você não pode alterar seu próprio papel.'
            }, status=400)
        
        with transaction.atomic():
            # Salva o papel antigo para o log
            papel_anterior = user.role
            
            # Atualiza o papel do usuário
            user.role = novo_papel
            
            # Configura flags de superusuário e staff conforme necessário
            if novo_papel == 'SUPERUSER':
                user.is_superuser = True
                user.is_staff = True
            else:
                user.is_superuser = False
                user.is_staff = (novo_papel == 'GERENTE')
            
            user.save()
            
            # Atualiza os grupos do usuário
            user.groups.clear()
            
            if novo_papel == 'GERENTE':
                grupo, _ = Group.objects.get_or_create(name='Usuário Gerente')
                user.groups.add(grupo)
            elif novo_papel == 'EVENTOS':
                grupo, _ = Group.objects.get_or_create(name='Usuário de Eventos')
                user.groups.add(grupo)
            
            # Registra a mudança de papel
            if papel_anterior != novo_papel:
                PapelHistorico.objects.create(
                    usuario=user,
                    papel_anterior=papel_anterior,
                    novo_papel=novo_papel,
                    alterado_por=request.user
                )
            
            return JsonResponse({
                'success': True,
                'message': f'Papel do usuário atualizado para {user.get_role_display()} com sucesso!',
                'novo_papel': user.get_role_display()
            })
            
    except get_user_model().DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Usuário não encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

from django.http import JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
import json

@require_http_methods(["POST"])
@login_required
@user_passes_test(lambda u: u.is_staff)
def toggle_user_status(request, user_id):
    """
    Alterna o status (ativo/inativo) de um usuário.
    
    Permissões:
    - Apenas superusuários ou gerentes podem ativar/desativar usuários
    - Não é possível desativar a si mesmo
    - Não é possível desativar superusuários (a menos que seja outro superusuário)
    """
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({
            'success': False,
            'message': 'Acesso negado. Você não tem permissão para executar esta ação.'
        }, status=403)

    try:
        User = get_user_model()
        user = User.objects.get(pk=user_id)
        
        # Não permitir que usuários desativem a si mesmos
        if user == request.user:
            return JsonResponse({
                'success': False,
                'message': 'Você não pode alterar seu próprio status.'
            }, status=400)
        
        # Apenas superusuários podem desativar outros superusuários
        if user.is_superuser and not request.user.is_superuser:
            return JsonResponse({
                'success': False,
                'message': 'Apenas superusuários podem alterar o status de outros superusuários.'
            }, status=403)
        
        # Alterna o status do usuário
        user.is_active = not user.is_active
        user.save()
        
        # Registrar a ação no log
        LogEntry.objects.log_action(
            user_id=request.user.id,
            content_type_id=ContentType.objects.get_for_model(user).id,
            object_id=user.id,
            object_repr=str(user),
            action_flag=CHANGE,
            change_message=f'Status alterado para {"Ativo" if user.is_active else "Inativo"}.'
        )
        
        return JsonResponse({
            'success': True,
            'is_active': user.is_active,
            'message': f'Usuário {user.get_full_name() or user.username} foi {"ativado" if user.is_active else "desativado"} com sucesso.'
        })
        
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Usuário não encontrado.'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao atualizar status do usuário: {str(e)}'
        }, status=500)

def atualizar_usuario(request, user_id):
    """
    Atualiza as informações do usuário e perfil via AJAX.
    
    Permissões:
    - Superusuário: Pode atualizar qualquer usuário
    - Gerente: Pode atualizar qualquer usuário, exceto superusuários
    - Usuário: Pode atualizar apenas o próprio perfil
    """
    try:
        # Obtém o usuário que está sendo atualizado
        user = get_object_or_404(get_user_model().objects.select_related('perfil'), id=user_id)
        
        # Verifica permissões
        if not request.user.is_superuser:  # Apenas superusuários podem editar outros usuários
            if request.user != user:  # Usuários não-super só podem editar a si mesmos
                return JsonResponse({
                    'success': False,
                    'message': 'Você não tem permissão para atualizar este usuário.'
                }, status=403)
        
        # Get POST data
        data = request.POST.dict()
        
        # Track changed fields
        changed_fields = []
        
        # Update basic user info
        if 'nome_completo' in data and data['nome_completo']:
            names = data['nome_completo'].split(' ', 1)
            if user.first_name != names[0] or user.last_name != (names[1] if len(names) > 1 else ''):
                user.first_name = names[0]
                user.last_name = names[1] if len(names) > 1 else ''
                changed_fields.append('nome_completo')
        
        if 'email' in data and user.email != data['email']:
            user.email = data['email']
            changed_fields.append('email')
        
        password_changed = False
        if 'nova_senha' in data and data['nova_senha']:
            user.set_password(data['nova_senha'])
            password_changed = True
            changed_fields.append('senha')
        
        if changed_fields:
            user.save()
        
        # Update profile info if exists
        if hasattr(user, 'perfil'):
            perfil = user.perfil
            perfil_changed = False
            
            profile_fields = {
                'genero': 'genero',
                'data_nascimento': 'data_nascimento',
                'telefone': 'telefone'
            }
            
            for field, data_field in profile_fields.items():
                if data_field in data and getattr(perfil, field, None) != data[data_field]:
                    setattr(perfil, field, data[data_field])
                    perfil_changed = True
                    changed_fields.append(field)
            
            # Handle boolean field
            telefone_whatsapp = data.get('telefone_whatsapp') == 'on'
            if perfil.telefone_whatsapp != telefone_whatsapp:
                perfil.telefone_whatsapp = telefone_whatsapp
                perfil_changed = True
                changed_fields.append('telefone_whatsapp')
            
            if perfil_changed:
                perfil.save()
        
        # Prepare response data
        response_data = {
            'status': 'success',
            'message': 'Dados atualizados com sucesso!',
            'redirect': reverse('admin_personalizado:detalhes_usuario', args=[user.id]),
            'password_changed': password_changed
        }
        
        return JsonResponse(response_data)
        
    except User.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Usuário não encontrado.'
        }, status=404)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Erro ao atualizar usuário: {str(e)}'
        }, status=500)