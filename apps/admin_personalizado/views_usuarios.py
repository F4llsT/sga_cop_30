from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
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

def is_superuser(user):
    """Verifica se o usuário é superusuário."""
    return user.is_superuser

def is_gerente(user):
    """Verifica se o usuário é gerente."""
    return user.groups.filter(name='Gerente').exists() or user.is_superuser
# No arquivo views_usuarios.py
@staff_member_required
@login_required
@user_passes_test(lambda u: is_superuser(u) or is_gerente(u))
def detalhes_usuario(request, user_id):
    """Exibe os detalhes completos de um usuário."""
    usuario = get_object_or_404(get_user_model(), id=user_id)
    
    # Verifica se o usuário tem permissão para ver os detalhes
    if not (request.user.is_superuser or is_gerente(request.user) or request.user == usuario):
        return HttpResponseForbidden("Você não tem permissão para acessar esta página.")
    
    # Obtém os grupos disponíveis, exceto o grupo de superusuários
    papeis_disponiveis = Group.objects.exclude(name='Superusuário')
    
    # Se o usuário for superusuário, adiciona uma entrada especial
    if usuario.is_superuser:
        papeis_disponiveis = list(papeis_disponiveis)  # Converte para lista para poder adicionar
        papeis_disponiveis.append({'id': 'superuser', 'name': 'Superusuário'})
    
    context = {
        'usuario': usuario,
        'papeis_disponiveis': papeis_disponiveis,
        'agora': timezone.now(),
    }
    return render(request, 'admin_personalizado/usuarios/usuario_detalhes.html', context)
@require_http_methods(["POST"])
@staff_member_required
@login_required
@user_passes_test(lambda u: u.is_superuser or is_gerente(u))
def alterar_papel_usuario(request, user_id):
    """Altera o papel de um usuário."""
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Usuário não autenticado'}, status=401)
    
    try:
        data = json.loads(request.body)
        novo_papel_id = data.get('novo_papel')
        
        if not novo_papel_id:
            return JsonResponse({'status': 'error', 'message': 'ID do papel não fornecido'}, status=400)
        
        usuario = get_user_model().objects.get(id=user_id)
        
        # Verifica se o usuário atual tem permissão para fazer a alteração
        if not (request.user.is_superuser or (is_gerente(request.user) and not usuario.is_superuser)):
            return JsonResponse({
                'status': 'error', 
                'message': 'Você não tem permissão para alterar este usuário'
            }, status=403)
        
        # Obtém o nome do papel anterior
        papel_anterior = usuario.groups.first().name if usuario.groups.exists() else 'Nenhum'
        
        with transaction.atomic():
            # Remove todos os grupos atuais
            usuario.groups.clear()
            
            # Adiciona o novo grupo se não for 'nenhum'
            if novo_papel_id != 'nenhum':
                novo_grupo = Group.objects.get(id=novo_papel_id)
                usuario.groups.add(novo_grupo)
                novo_papel_nome = novo_grupo.name
            else:
                novo_papel_nome = 'Nenhum'
            
            # Registra a alteração no histórico
            PapelHistorico.objects.create(
                usuario=usuario,
                papel_anterior=papel_anterior,
                novo_papel=novo_papel_nome,
                alterado_por=request.user
            )
            
            # Se o usuário alterado for o próprio usuário logado, força o refresh da sessão
            if usuario == request.user:
                update_session_auth_hash(request, usuario)
            
            return JsonResponse({
                'status': 'success',
                'message': f'Papel alterado com sucesso para {novo_papel_nome}',
                'novo_papel': novo_papel_nome
            })
            
    except get_user_model().DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Usuário não encontrado'}, status=404)
    except Group.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Papel não encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Erro ao alterar papel: {str(e)}'}, status=500)

@staff_member_required
@login_required
@user_passes_test(lambda u: is_superuser(u) or is_gerente(u))
def listar_usuarios(request):
    User = get_user_model()  # Adicione esta linha
    usuarios = User.objects.all().order_by('-date_joined')
    total_usuarios = User.objects.count()
    ativos_count = User.objects.filter(is_active=True).count()
    inativos_count = User.objects.filter(is_active=False).count()
    admins_count = User.objects.filter(is_superuser=True).count()
  
    # Paginação
    paginator = Paginator(usuarios, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'object_list': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'total_usuarios': total_usuarios,
        'ativos_count': ativos_count,
        'inativos_count': inativos_count,
        'admins_count': admins_count,
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

@staff_member_required
@login_required
@user_passes_test(lambda u: is_superuser(u) or is_gerente(u))
def detalhes_usuario(request, user_id):
    """Exibe os detalhes completos de um usuário."""
    User = get_user_model()
    user = get_object_or_404(User, id=user_id)
    
    # Verifica se o usuário atual tem permissão para ver este usuário
    if not (request.user.is_superuser or (is_gerente(request.user) and not user.is_superuser)):
        return HttpResponseForbidden("Você não tem permissão para acessar esta página.")
    
    # Obtém o papel atual do usuário
    user_role = 'Administrador' if user.is_superuser else \
               'Gerente' if user.groups.filter(name='Gerente').exists() else \
               'Usuário'
    
    # Obtém o histórico de alterações de papel
    role_history = LogEntryManager.get_user_role_history(user)
    
    context = {
        'usuario': user,
        'user_role': user_role,
        'role_history': role_history,
        'can_edit': request.user.is_superuser or (is_gerente(request.user) and not user.is_superuser)
    }
    
    return render(request, 'admin_personalizado/usuarios/usuario_detalhes.html', context)

@require_http_methods(["POST"])
@staff_member_required
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
@staff_member_required
@login_required
@user_passes_test(lambda u: is_superuser(u) or is_gerente(u))
def atualizar_papel_usuario(request, user_id):
    """Atualiza o papel de um usuário via AJAX."""
    if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'message': 'Requisição inválida'}, status=400)
    
    try:
        user = get_user_model().objects.get(pk=user_id)
        papel = request.POST.get('papel')
        
        # Verifica se o usuário não está tentando modificar a si mesmo
        if user == request.user:
            return JsonResponse({
                'success': False, 
                'message': 'Você não pode alterar seu próprio papel.'
            }, status=400)
        
        with transaction.atomic():
            # Remove todos os grupos atuais
            user.groups.clear()
            
            # Aplica o novo papel
            if papel == 'superuser':
                user.is_superuser = True
                user.is_staff = True
                user.save()
            else:
                user.is_superuser = False
                user.is_staff = (papel == 'gerente')  # Apenas gerentes têm acesso ao admin
                user.save()
                
                if papel in ['gerente', 'eventos']:
                    grupo, _ = Group.objects.get_or_create(name=papel.capitalize())
                    user.groups.add(grupo)
            
            return JsonResponse({
                'success': True,
                'message': f'Papel do usuário atualizado para {papel} com sucesso!',
                'novo_papel': papel
            })
            
    except get_user_model().DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Usuário não encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

from django.http import JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.utils import timezone
import json

@require_http_methods(["POST"])
@staff_member_required
@login_required
@transaction.atomic
def atualizar_usuario(request, user_id):
    """Atualiza as informações do usuário e perfil via AJAX."""
    try:
        # Get the user being updated
        user = get_user_model().objects.select_related('perfil').get(id=user_id)
        
        # Check permissions
        if not (request.user.is_superuser or is_gerente(request.user) or request.user == user):
            return JsonResponse({
                'status': 'error',
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