from django.db import models

# Create your models here.
# apps/admin_personalizado/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class NotificacaoPersonalizada(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('enviada', 'Enviada'),
        ('erro', 'Erro no Envio'),
    ]
    
    titulo = models.CharField(max_length=200)
    mensagem = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pendente')
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_envio = models.DateTimeField(null=True, blank=True)
    criado_por = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='notificacoes_criadas'
    )
    
    class Meta:
        verbose_name = 'Notificação Personalizada'
        verbose_name_plural = 'Notificações Personalizadas'
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"{self.titulo}"
    
    def enviar_notificacoes(self):
        from django.contrib.auth.models import Group
        from apps.notificacoes.models import Notificacao
        
        try:
            # Obter todos os usuários
            usuarios = User.objects.all()
            
            # Criar notificações para cada usuário
            for usuario in usuarios:
                Notificacao.objects.create(
                    usuario=usuario,
                    titulo=self.titulo,
                    mensagem=self.mensagem,
                    tipo='info'  # Valor padrão já que removemos o campo tipo
                )
            
            # Atualizar status e data de envio
            self.status = 'enviada'
            self.data_envio = timezone.now()
            self.save()
            
            return True, f"Notificações enviadas para {usuarios.count()} usuários."
            
        except Exception as e:
            self.status = 'erro'
            self.save()
            return False, str(e)