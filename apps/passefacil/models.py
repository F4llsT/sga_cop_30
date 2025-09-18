# apps/passefacil/models.py
from django.db import models
from django.contrib.auth import get_user_model
import uuid
from django.utils import timezone

User = get_user_model()

class PasseFacil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='passe_facil')
    codigo = models.UUIDField(default=uuid.uuid4, editable=False)
    data_atualizacao = models.DateTimeField(auto_now=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"Passe Fácil - {self.user.get_full_name() or self.user.username}"

    @property
    def tempo_restante(self):
        tempo_decorrido = timezone.now() - self.data_atualizacao
        return max(60 - int(tempo_decorrido.total_seconds()), 0)

    def gerar_novo_codigo(self):
        self.codigo = uuid.uuid4()
        self.data_atualizacao = timezone.now()
        self.save()
        return self.codigo

    def validar_codigo(self, codigo):
        if str(self.codigo) == str(codigo) and self.ativo:
            # Registrar a validação
            ValidacaoQRCode.objects.create(
                passe_facil=self,
                codigo=codigo,
                valido=True
            )
            return True
        return False

class ValidacaoQRCode(models.Model):
    passe_facil = models.ForeignKey(PasseFacil, on_delete=models.CASCADE, related_name='validacoes')
    codigo = models.CharField(max_length=36)
    data_validacao = models.DateTimeField(auto_now_add=True)
    valido = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-data_validacao']
        verbose_name = 'Validação de QR Code'
        verbose_name_plural = 'Validações de QR Code'

    def __str__(self):
        status = "Válido" if self.valido else "Inválido"
        return f"Validação {self.id} - {self.passe_facil.user} - {status} - {self.data_validacao}"