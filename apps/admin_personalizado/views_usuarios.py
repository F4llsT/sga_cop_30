from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.models import Group
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction

def is_superuser(user):
    """Verifica se o usuário é superusuário."""
    return user.is_superuser

def is_gerente(user):
    """Verifica se o usuário é gerente."""
    return user.groups.filter(name='Gerente').exists() or user.is_superuser
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
    
@require_POST
@staff_member_required
@login_required
@user_passes_test(is_superuser)
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
