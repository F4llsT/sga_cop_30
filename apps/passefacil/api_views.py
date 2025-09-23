from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.views.decorators.csrf import csrf_exempt
import logging

from .services import PasseFacilService
from .models import ValidacaoQRCode, PasseFacil

logger = logging.getLogger(__name__)

class ValidarQRCodeThrottle(UserRateThrottle):
    scope = 'qr_validation'

class ValidarQRCodeAPIView(APIView):
    """
    API para validação de QR Code com autenticação de sessão e rate limiting
    """
    permission_classes = [IsAuthenticated]  # Usa a autenticação de sessão do Django
    throttle_classes = [ValidarQRCodeThrottle]
    
    @method_decorator(cache_page(5))  # Cache de 5 segundos
    @method_decorator(vary_on_cookie)
    def get(self, request, format=None):
        """Valida um código QR"""
        codigo = request.query_params.get('codigo')
        if not codigo:
            return Response(
                {'erro': 'Código não fornecido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Obtém o endereço IP do cliente
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        ip_address = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
        
        try:
            # Valida o código usando o serviço
            valido, mensagem = PasseFacilService.validar_codigo(codigo, request.user)

            # Garante que o usuário possui um PasseFacil para registrar a tentativa
            passe_facil, _ = PasseFacil.objects.get_or_create(user=request.user, defaults={'ativo': True})

            # Registra a tentativa de validação
            ValidacaoQRCode.objects.create(
                passe_facil=passe_facil,
                codigo=codigo,
                valido=valido,
                ip_address=ip_address
            )
            
            if valido:
                nome_preferido = (getattr(request.user, 'nome', '') or request.user.get_full_name() or '').strip() or request.user.email
                return Response({
                    'valido': True,
                    'mensagem': mensagem,
                    'usuario': {
                        'nome': nome_preferido,
                        'email': request.user.email,
                        'matricula': getattr(request.user, 'matricula', '')
                    }
                })
            else:
                return Response(
                    {'valido': False, 'erro': mensagem}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            logger.error(f"Erro ao validar QR Code: {str(e)}")
            return Response(
                {'erro': 'Erro ao processar a validação'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class GerarQRCodeAPIView(APIView):
    """
    API para geração de QR Code com autenticação de sessão
    """
    permission_classes = [IsAuthenticated]  # Usa a autenticação de sessão do Django
    
    def get(self, request, format=None):
        """Gera um novo QR Code para o usuário"""
        try:
            # Obtém ou cria o passe do usuário
            passe, created = PasseFacil.objects.get_or_create(
                user=request.user,
                defaults={'ativo': True}
            )
            
            # Se o passe existe mas está inativo, ativa
            if not passe.ativo:
                passe.ativo = True
                passe.save()
            
            # Gera um novo código
            novo_codigo = passe.gerar_novo_codigo()
            
            return Response({
                'status': 'success',
                'codigo': str(novo_codigo),
                'data_atualizacao': passe.data_atualizacao.isoformat(),
                'novo': created
            })
            
        except Exception as e:
            logger.error(f"Erro ao gerar QR Code: {str(e)}")
            return Response(
                {'erro': 'Erro ao gerar QR Code'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UltimasValidacoesAPIView(APIView):
    """
    API para buscar as validações recentes do usuário
    """
    permission_classes = [IsAuthenticated]  # Usa a autenticação de sessão do Django
    
    def get(self, request, format=None):
        """Retorna as últimas validações do usuário"""
        try:
            # Obtém o passe do usuário
            passe = PasseFacil.objects.filter(user=request.user).first()
            if not passe:
                return Response({
                    'status': 'success',
                    'validacoes': []
                })
            
            # Busca as últimas 5 validações
            validacoes = ValidacaoQRCode.objects.filter(
                passe_facil=passe,
                valido=True
            ).order_by('-data_validacao')[:5]
            
            # Formata os dados para a resposta
            validacoes_data = [{
                'id': v.id,
                'data_validacao': v.data_validacao.isoformat(),
                'valido': v.valido,
                'ip_address': v.ip_address or 'Local desconhecido'
            } for v in validacoes]
            
            return Response({
                'status': 'success',
                'validacoes': validacoes_data
            })
            
        except Exception as e:
            logger.error(f"Erro ao buscar validações: {str(e)}")
            return Response(
                {'erro': 'Erro ao buscar validações'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
