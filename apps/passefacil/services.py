import pyotp
import qrcode
import base64
import logging
from io import BytesIO
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from .models import PasseFacil, ValidacaoQRCode

logger = logging.getLogger(__name__)

class PasseFacilService:
    """
    Serviço para gerenciar a lógica de negócios do Passe Fácil
    """
    
    # Tempo de expiração do código TOTP (em segundos)
    TOTP_INTERVAL = 30
    
    @classmethod
    def get_or_create_passe_facil(cls, user):
        """Obtém ou cria um Passe Fácil para o usuário"""
        passe, created = PasseFacil.objects.get_or_create(
            user=user,
            defaults={'ativo': True}
        )
        return passe, created
    
    @classmethod
    def gerar_codigo_totp(cls, user):
        """Gera um novo código TOTP para o usuário"""
        # Usamos o email do usuário como base para o segredo
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret, interval=cls.TOTP_INTERVAL)
        
        # Atualiza o Passe Fácil com o novo segredo
        passe, _ = cls.get_or_create_passe_facil(user)
        passe.secret_totp = secret
        passe.ultima_geracao = timezone.now()
        passe.save()
        
        # Retorna o código atual
        return totp.now()
    
    @classmethod
    def gerar_qr_code(cls, user, issuer_name="SGA COP 30"):
        """Gera um QR Code para autenticação TOTP"""
        # Obtém ou cria o Passe Fácil
        passe, _ = cls.get_or_create_passe_facil(user)
        
        # Se não tiver um segredo TOTP, gera um novo
        if not hasattr(passe, 'secret_totp') or not passe.secret_totp:
            cls.gerar_codigo_totp(user)
            passe.refresh_from_db()
        
        # Gera a URL para o aplicativo autenticador
        totp = pyotp.TOTP(passe.secret_totp, interval=cls.TOTP_INTERVAL)
        provisioning_uri = totp.provisioning_uri(
            name=user.email,
            issuer_name=issuer_name
        )
        
        # Gera o QR Code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Converte para base64 para exibição no template
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    @classmethod
    def validar_codigo(cls, codigo, user):
        """Valida um código TOTP para o usuário"""
        try:
            passe = PasseFacil.objects.get(user=user)
            
            # Verifica se o passe está ativo
            if not passe.ativo:
                return False, "Passe Fácil desativado"
                
            # Verifica se o código é válido
            totp = pyotp.TOTP(passe.secret_totp, interval=cls.TOTP_INTERVAL)
            is_valid = totp.verify(codigo)
            
            # Registra a tentativa de validação
            ValidacaoQRCode.objects.create(
                passe_facil=passe,
                codigo=codigo,
                valido=is_valid
            )
            
            if is_valid:
                return True, "Código válido"
            return False, "Código inválido ou expirado"
            
        except PasseFacil.DoesNotExist:
            return False, "Passe Fácil não encontrado"
        except Exception as e:
            logger.error(f"Erro ao validar código: {str(e)}")
            return False, "Erro ao processar a validação"
