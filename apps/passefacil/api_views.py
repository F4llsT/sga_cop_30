from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
import logging

from .services import PasseFacilService
from .models import ValidacaoQRCode

logger = logging.getLogger(__name__)

class ValidarQRCodeThrottle(UserRateThrottle):
    scope = 'qr_validation'

class ValidarQRCodeAPIView(APIView):
    """
    API para validação de QR Code com autenticação JWT e rate limiting
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
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
            
            # Registra a tentativa de validação
            ValidacaoQRCode.objects.create(
                passe_facil=request.user.passe_facil,
                codigo=codigo,
                valido=valido,
                ip_address=ip_address
            )
            
            if valido:
                return Response({
                    'valido': True,
                    'mensagem': mensagem,
                    'usuario': {
                        'nome': request.user.get_full_name(),
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
    API para geração de QR Code com autenticação JWT
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, format=None):
        """Gera um novo QR Code para o usuário"""
        try:
            # Gera o QR Code usando o serviço
            qr_code_data = PasseFacilService.gerar_qr_code(request.user)
            
            return Response({
                'qr_code': qr_code_data,
                'validade_segundos': PasseFacilService.TOTP_INTERVAL
            })
            
        except Exception as e:
            logger.error(f"Erro ao gerar QR Code: {str(e)}")
            return Response(
                {'erro': 'Erro ao gerar QR Code'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
