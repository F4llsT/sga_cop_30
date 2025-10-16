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
@staff_member_required
@login_required
@user_passes_test(lambda u: is_superuser(u) or is_gerente(u))
def detalhes_usuario(request, user_id):
    """Exibe os detalhes completos de um usuário."""
    usuario = get_object_or_404(get_user_model(), id=user_id)
    
    # Verifica se o usuário tem permissão para ver os detalhes
    if not (request.user.is_superuser or request.user == usuario or is_gerente(request.user)):
        return HttpResponseForbidden("Você não tem permissão para acessar esta página.")
    
    # Obtém o histórico de alterações de papel
    historico_papeis = getattr(usuario, 'historico_papeis', [])
    
    context = {
        'usuario': usuario,
        'historico_papeis': historico_papeis,
        'papeis_disponiveis': Group.objects.all(),
        'agora': timezone.now(),
    }
    return render(request, 'admin_personalizado/usuarios/usuario_detalhes.html', context)

@staff_member_required
@login_required
@user_passes_test(lambda u: is_superuser(u) or is_gerente(u))
@require_http_methods(["POST"])
def alterar_papel_usuario(request, user_id):
    """Altera o papel de um usuário e registra no histórico."""
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'error', 'message': 'Usuário não autenticado'}, status=401)
    
    try:
        data = json.loads(request.body)
        novo_papel_id = data.get('novo_papel')
        
        if not novo_papel_id:
            return JsonResponse({'status': 'error', 'message': 'ID do papel não fornecido'}, status=400)
        
        usuario = get_user_model().objects.get(id=user_id)
        papel_anterior = usuario.groups.first().name if usuario.groups.exists() else 'Nenhum'
        
        with transaction.atomic():
            # Remove todos os grupos atuais
            usuario.groups.clear()
            
            # Adiciona o novo grupo
            if novo_papel_id != 'nenhum':
                novo_grupo = Group.objects.get(id=novo_papel_id)
                usuario.groups.add(novo_grupo)
            
            # Registra a alteração no histórico
            PapelHistorico.objects.create(
                usuario=usuario,
                papel_anterior=papel_anterior,
                novo_papel=novo_grupo.name if novo_papel_id != 'nenhum' else 'Nenhum',
                alterado_por=request.user
            )
            
            return JsonResponse({
                'status': 'success',
                'message': 'Papel do usuário atualizado com sucesso!',
                'novo_papel': novo_grupo.name if novo_papel_id != 'nenhum' else 'Nenhum'
            })
            
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

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
@csrf_exempt  # Only for testing, use proper CSRF in production
@staff_member_required
@login_required
@require_http_methods(["POST"])
@csrf_exempt  # For testing only - remove in production and use proper CSRF
@transaction.atomic
def atualizar_usuario(request, user_id):
    """Atualiza as informações do usuário e perfil via AJAX."""
    try:
        # Get the user being updated
        user = get_user_model().objects.select_related('perfil').get(id=user_id)
        
        # Check if the current user has permission to update this user
        if not (request.user.is_superuser or is_gerente(request.user) or request.user == user):
            return JsonResponse({
                'status': 'error',
                'message': 'Você não tem permissão para atualizar este usuário.'
            }, status=403)
        
        # Get POST data
        data = request.POST.dict()
        
        # Update basic user info
        if 'nome_completo' in data and data['nome_completo']:
            names = data['nome_completo'].split(' ', 1)
            user.first_name = names[0]
            user.last_name = names[1] if len(names) > 1 else ''
        
        if 'email' in data:
            user.email = data['email']
        
        if 'nova_senha' in data and data['nova_senha']:
            user.set_password(data['nova_senha'])
        
        user.save()
        
        # Update profile info if exists
        if hasattr(user, 'perfil'):
            perfil = user.perfil
            
            if 'genero' in data:
                perfil.genero = data['genero']
            
            if 'data_nascimento' in data and data['data_nascimento']:
                perfil.data_nascimento = data['data_nascimento']
            
            if 'telefone' in data:
                perfil.telefone = data['telefone']
            
            perfil.telefone_whatsapp = 'telefone_whatsapp' in data
            
            # Update address fields if they exist in the model
            address_fields = [
                'cep', 'logradouro', 'numero', 'complemento',
                'bairro', 'cidade', 'estado'
            ]
            
            for field in address_fields:
                if field in data:
                    setattr(perfil, field, data[field])
            
            perfil.save()
        
        # Log the change
        LogEntryManager.log_user_update(
            user=user,
            request_user=request.user,
            changed_fields=[k for k in data.keys() if k != 'csrfmiddlewaretoken']
        )
        
        # Prepare response data
        response_data = {
            'status': 'success',
            'message': 'Dados atualizados com sucesso!',
            'nome_completo': user.get_full_name(),
            'email': user.email,
        }
        
        # Add profile data to response if profile exists
        if hasattr(user, 'perfil'):
            perfil = user.perfil
            profile_data = {
                'genero': perfil.genero,
                'data_nascimento': perfil.data_nascimento.isoformat() if perfil.data_nascimento else None,
                'telefone': perfil.telefone,
                'telefone_whatsapp': perfil.telefone_whatsapp,
                'cep': getattr(perfil, 'cep', ''),
                'logradouro': getattr(perfil, 'logradouro', ''),
                'numero': getattr(perfil, 'numero', ''),
                'complemento': getattr(perfil, 'complemento', ''),
                'bairro': getattr(perfil, 'bairro', ''),
                'cidade': getattr(perfil, 'cidade', ''),
                'estado': getattr(perfil, 'estado', '')
            }
            response_data.update(profile_data)
        
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

