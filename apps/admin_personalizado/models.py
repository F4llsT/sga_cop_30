from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction

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
        from django.contrib.auth import get_user_model
        from apps.notificacoes.models import Notificacao
        
        User = get_user_model()
        
        try:
            # Get all active users
            usuarios = User.objects.filter(is_active=True)
            total_usuarios = usuarios.count()
            notificacoes_criadas = 0
            
            # Create notifications in a transaction
            with transaction.atomic():
                for usuario in usuarios:
                    Notificacao.objects.create(
                        usuario=usuario,
                        titulo=self.titulo,
                        mensagem=self.mensagem,
                        tipo='info'  # Default type since we removed the tipo field
                    )
                    notificacoes_criadas += 1
                
                # Update notification status and save
                self.status = 'enviada'
                self.data_envio = timezone.now()
                self.save()
            
            return True, f"Notificações enviadas para {notificacoes_criadas} de {total_usuarios} usuários."
            
        except Exception as e:
            self.status = 'erro'
            self.save()
            return False, f"Erro ao enviar notificações: {str(e)}"