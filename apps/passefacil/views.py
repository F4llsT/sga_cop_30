# apps/passefacil/views.py
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import PasseFacil, ValidacaoQRCode
from apps.notificacoes.models import Notificacao
from apps.notificacoes.push import send_push_to_user
import logging
import io
import uuid
import qrcode
import json

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["GET"])
def validar_qr_code(request):
    codigo = request.GET.get('codigo', '')
    ip_address = request.META.get('HTTP_X_FORWARDED_FOR') or request.META.get('REMOTE_ADDR')

    # Validação básica de entrada
    if not codigo:
        return JsonResponse({
            'valido': False,
            'mensagem': 'Código não fornecido.'
        }, status=400)

    try:
        # Aceita código com ou sem hífens
        try:
            codigo_uuid = uuid.UUID(codigo)
        except ValueError:
            codigo_uuid = uuid.UUID(hex=codigo.replace('-', ''))

        passe = PasseFacil.objects.get(codigo=codigo_uuid)
        
        # Verifica se o passe está ativo
        if not passe.ativo:
            return JsonResponse({
                'valido': False,
                'mensagem': 'Passe Fácil não está ativo.'
            })
            
        # Dados do usuário (preferindo campo "nome" do usuário customizado)
        user = passe.user
        nome_preferido = (getattr(user, 'nome', '') or user.get_full_name() or '').strip() or user.email

        # Registra a validação
        validacao = ValidacaoQRCode(
            passe_facil=passe,
            codigo=str(codigo_uuid),
            valido=True,
            ip_address=ip_address
        )
        validacao.save()
        
        # Cria notificação para o usuário
        try:
            notificacao = Notificacao.objects.create(
                titulo='Passe Fácil Validado',
                mensagem=f'Seu código foi validado em {timezone.localtime().strftime("%d/%m/%Y %H:%M")} (IP: {ip_address})',
                tipo='success',
                criado_por=request.user if request.user.is_authenticated else None
            )
            
            # Adiciona o usuário à notificação
            notificacao.usuarios.add(user)
            
            # Envia notificação push se o usuário estiver online
            try:
                send_push_to_user(
                    user_external_id=str(user.id),
                    title='Passe Fácil Validado',
                    message=f'Seu código foi validado em {timezone.localtime().strftime("%d/%m/%Y %H:%M")}'
                )
            except Exception as push_error:
                logger.warning(f"Erro ao enviar notificação push: {push_error}")
        except Exception as notif_error:
            logger.warning(f"Erro ao criar notificação: {notif_error}")
        
        return JsonResponse({
            'valido': True,
            'mensagem': f'Passe válido para {nome_preferido}',
            'usuario': {
                'id': user.id,
                'nome': nome_preferido,
                'email': user.email,
            },
            'codigo': str(codigo_uuid),
            'notificacao_id': notificacao.id
        })
        
    except PasseFacil.DoesNotExist:
        # Registra tentativa de validação inválida
        ValidacaoQRCode.objects.create(
            codigo=str(codigo),
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
        print(f"Usuário: {getattr(request.user, 'email', 'sem-email')} (ID: {request.user.id})")
        
        # Verifica se é uma requisição AJAX para mostrar loading
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        # Obtém ou cria o PasseFacil se não existir
        if not hasattr(request.user, 'passe_facil'):
            passe_facil = PasseFacil.objects.create(
                user=request.user,
                ativo=True,
                codigo=uuid.uuid4()
            )
            print(f"Novo PasseFacil criado com código: {passe_facil.codigo}")
            
            # Adiciona mensagem de sucesso
            if not is_ajax:
                messages.success(request, "Seu Passe Fácil foi criado com sucesso!")
        else:
            passe_facil = request.user.passe_facil
            print(f"PasseFacil existente encontrado. Código: {passe_facil.codigo}")
            
            # Se não tiver código, gera um novo
            if not passe_facil.codigo:
                passe_facil.codigo = uuid.uuid4()
                passe_facil.save()
                print(f"Código gerado para PasseFacil existente: {passe_facil.codigo}")
        
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
    if not hasattr(request.user, 'passe_facil'):
        # Redireciona para gerar o QR Code se o usuário não tiver um PasseFacil
        return redirect('passefacil:gerar_qr_code_dinamico')
    
    # Adiciona mensagem de sucesso se for um redirecionamento após a geração
    if 'qr_gerado' in request.session:
        messages.success(request, "QR Code gerado com sucesso!")
        del request.session['qr_gerado']
    
    context = {
        'passe_facil': request.user.passe_facil,
        'ultimas_validacoes': ValidacaoQRCode.objects.filter(
            passe_facil=request.user.passe_facil,
            valido=True
        ).order_by('-data_validacao')[:5]
    }
    return render(request, 'passefacil/meu_qr_code.html', context)

@login_required
@require_http_methods(["POST"])
def atualizar_qr_code(request):
    """Gera um novo código UUID para o PasseFacil do usuário e retorna JSON.
    Usado pelo botão 'Atualizar QR Code' no template passe_facil.
    """
    try:
        # Obtém ou cria o passe
        if not hasattr(request.user, 'passe_facil'):
            passe = PasseFacil.objects.create(user=request.user, ativo=True, codigo=uuid.uuid4())
        else:
            passe = request.user.passe_facil

        # Gera novo código
        passe.codigo = uuid.uuid4()
        passe.data_atualizacao = timezone.now()
        passe.save()

        return JsonResponse({
            'status': 'success',
            'novo_codigo': str(passe.codigo).replace('-', ''),
            'tempo_restante': 60,
        })
    except Exception as e:
        logger.error(f"Erro ao atualizar QR Code: {e}")
        return JsonResponse({'status': 'error', 'mensagem': 'Falha ao atualizar QR Code'}, status=500)