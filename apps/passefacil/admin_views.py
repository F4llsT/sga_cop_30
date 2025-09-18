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
    
    context = {
        'validacoes_recentes': validacoes_recentes,
        'total_validacoes': total_validacoes,
        'validas': validas,
        'invalidas': invalidas,
    }
    return render(request, 'passefacil/admin/dashboard.html', context)

@user_passes_test(is_admin)
def validar_qr_code(request):
    if request.method == 'POST':
        codigo = request.POST.get('codigo')
        if not codigo:
            return JsonResponse({'valido': False, 'erro': 'Código não fornecido'}, status=400)
        
        try:
            passe = PasseFacil.objects.get(codigo=codigo)
            valido = passe.validar_codigo(codigo)
            
            return JsonResponse({
                'valido': valido,
                'usuario': {
                    'nome': str(passe.user.get_full_name() or passe.user.username),
                    'email': passe.user.email
                },
                'data_validacao': timezone.now().strftime('%d/%m/%Y %H:%M:%S')
            })
        except PasseFacil.DoesNotExist:
            # Registrar tentativa inválida
            ValidacaoQRCode.objects.create(
                codigo=codigo,
                valido=False,
                ip_address=request.META.get('REMOTE_ADDR')
            )
            return JsonResponse({'valido': False, 'erro': 'Código inválido'}, status=404)
    
    return JsonResponse({'erro': 'Método não permitido'}, status=405)