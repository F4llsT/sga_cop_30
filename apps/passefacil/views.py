# apps/passefacil/views.py
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import PasseFacil, ValidacaoQRCode
from django.utils import timezone
import logging
import io
import qrcode

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["GET"])
def validar_qr_code(request):
    codigo = request.GET.get('codigo', '')
    ip_address = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR')
    
    try:
        passe = PasseFacil.objects.get(codigo=codigo)
        
        # Verifica se o passe está ativo
        if not passe.ativo:
            return JsonResponse({
                'valido': False,
                'mensagem': 'Passe Fácil não está ativo.'
            })
            
        # Registra a validação
        validacao = ValidacaoQRCode(
            passe_facil=passe,
            codigo=codigo,
            valido=True,
            ip_address=ip_address
        )
        validacao.save()
        
        return JsonResponse({
            'valido': True,
            'mensagem': f'Passe válido para {passe.user.get_full_name() or passe.user.username}'
        })
        
    except PasseFacil.DoesNotExist:
        # Registra tentativa de validação inválida
        ValidacaoQRCode.objects.create(
            codigo=codigo,
            valido=False,
            ip_address=ip_address
        )
        return JsonResponse({
            'valido': False,
            'mensagem': 'Código QR inválido ou expirado.'
        })
    except Exception as e:
        logger.error(f"Erro ao validar QR Code: {str(e)}")
        return JsonResponse({
            'valido': False,
            'mensagem': 'Erro ao processar a validação.'
        }, status=500)

@login_required
def gerar_qr_code_dinamico(request):
    try:
        print("Tentando obter o passe fácil do usuário...")
        passe_facil = request.user.passe_facil
        print(f"Passe Fácil encontrado: {passe_facil}")
        
        if not passe_facil.ativo:
            print("Passe Fácil inativo")
            return HttpResponse("Passe inativo", status=403)

        print(f"Gerando QR Code para o código: {passe_facil.codigo}")
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(str(passe_facil.codigo))  
        qr.make(fit=True)

        print("Criando imagem do QR Code...")
        img = qr.make_image(fill_color="black", back_color="white")
        
        print("Preparando resposta...")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        print("Enviando resposta...")
        response = HttpResponse(buffer, content_type='image/png')
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response

    except PasseFacil.DoesNotExist:
        print("Erro: Passe Fácil não encontrado")
        return HttpResponse("Passe Fácil não encontrado.", status=404)
    except Exception as e:
        print(f"Erro inesperado ao gerar QR Code: {str(e)}")
        import traceback
        traceback.print_exc()
        return HttpResponse(f"Erro ao gerar QR Code: {str(e)}", status=500)

@login_required
def meu_qr_code_view(request):
    # Verifica se o usuário já tem um Passe Fácil
    if not hasattr(request.user, 'passe_facil'):
        # Cria um novo Passe Fácil para o usuário
        PasseFacil.objects.create(
            user=request.user,
            ativo=True
        )
        # Recarrega o usuário para garantir que o passe_facil esteja disponível
        request.user.refresh_from_db()
    
    return render(request, 'passefacil/meu_qr_code.html')