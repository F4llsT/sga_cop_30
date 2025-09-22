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
        print("\n=== Iniciando geração de QR Code ===")
        print(f"Usuário: {request.user.username} (ID: {request.user.id})")
        
        # Obtém ou cria o PasseFacil se não existir
        if not hasattr(request.user, 'passe_facil'):
            passe_facil = PasseFacil.objects.create(
                user=request.user,
                ativo=True,
                codigo=uuid.uuid4()
            )
            print(f"Novo PasseFacil criado com código: {passe_facil.codigo}")
        else:
            passe_facil = request.user.passe_facil
            print(f"PasseFacil existente encontrado. Código: {passe_facil.codigo}")
            
            # Se não tiver código, gera um novo
            if not passe_facil.codigo:
                passe_facil.codigo = uuid.uuid4()
                passe_facil.save()
                print(f"Novo código gerado para PasseFacil: {passe_facil.codigo}")
        
        if not passe_facil.ativo:
            print("ERRO: Passe Fácil está inativo")
            return HttpResponse("Passe inativo", status=403)

        # Converte o UUID para string e remove hífens para garantir consistência
        codigo_str = str(passe_facil.codigo).replace('-', '')
        print(f"Gerando QR Code para o código: {codigo_str}")
        
        # Cria o QR Code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(codigo_str)
        qr.make(fit=True)

        print("Criando imagem do QR Code...")
        img = qr.make_image(fill_color="black", back_color="white")
        
        print("Preparando resposta...")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        print("Enviando resposta...\n")
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
        # Cria um novo Passe Fácil para o usuário com um código gerado automaticamente
        passe = PasseFacil.objects.create(
            user=request.user,
            ativo=True,
            codigo=uuid.uuid4()  # Gera um novo UUID automaticamente
        )
        print(f"Novo PasseFacil criado com código: {passe.codigo}")
        # Recarrega o usuário para garantir que o passe_facil esteja disponível
        request.user.refresh_from_db()
    else:
        # Garante que o passe existente tenha um código
        passe = request.user.passe_facil
        if not passe.codigo:
            passe.codigo = uuid.uuid4()
            passe.save()
            print(f"Código gerado para PasseFacil existente: {passe.codigo}")
    
    # Debug: verifica o código atual
    codigo_atual = request.user.passe_facil.codigo
    print(f"Código atual para o usuário {request.user.username}: {codigo_atual}")
    
    # Adiciona o código ao contexto para depuração
    context = {
        'user': request.user,
        'codigo_passe': str(codigo_atual) if codigo_atual else 'NENHUM_CÓDIGO_GERADO',
        'usuario_nome': request.user.get_full_name() or request.user.username
    }
    
    return render(request, 'passefacil/meu_qr_code.html', context)