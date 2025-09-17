# apps/passefacil/models.py
from django.db import models
from django.contrib.auth import get_user_model
import uuid
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class PasseFacil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='passe_facil')
    codigo = models.UUIDField(default=uuid.uuid4, editable=False)
    data_atualizacao = models.DateTimeField(auto_now=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"Passe Fácil - {self.user.username}"

    @property
    def tempo_restante(self):
        tempo_decorrido = timezone.now() - self.data_atualizacao
        tempo_restante = max(60 - int(tempo_decorrido.total_seconds()), 0)
        return tempo_restante

    def gerar_novo_codigo(self):
        self.codigo = uuid.uuid4()
        self.save()
        return self.codigo