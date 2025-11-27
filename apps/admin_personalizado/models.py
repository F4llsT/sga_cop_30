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


class RedeSocial(models.Model):
    nome = models.CharField(max_length=50)
    url = models.URLField(max_length=500)
    icone = models.CharField(max_length=50, help_text="Classe do FontAwesome (ex: fa-brands fa-twitter)")
    ativo = models.BooleanField(default=True)
    ordem = models.PositiveIntegerField(default=0, help_text="Ordem de exibição")
    
    class Meta:
        verbose_name = 'Rede Social'
        verbose_name_plural = 'Redes Sociais'
        ordering = ['ordem', 'nome']
    
    def __str__(self):
        return self.nome


class Contato(models.Model):
    tipo_contato = models.CharField(max_length=50, help_text="Ex: Email, Telefone, Endereço")
    valor = models.CharField(max_length=255, help_text="Ex: contato@cop30.com.br, (81) 1234-5678")
    icone = models.CharField(max_length=50, help_text="Classe do FontAwesome (ex: fa-solid fa-envelope)")
    ativo = models.BooleanField(default=True)
    ordem = models.PositiveIntegerField(default=0, help_text="Ordem de exibição")
    
    class Meta:
        verbose_name = 'Contato'
        verbose_name_plural = 'Contatos'
        ordering = ['ordem', 'tipo_contato']
    
    def __str__(self):
        return f"{self.tipo_contato}: {self.valor}"


class ConfiguracaoSite(models.Model):
    chave = models.CharField(max_length=100, unique=True)
    valor = models.TextField()
    descricao = models.CharField(max_length=255, blank=True)
    
    class Meta:
        verbose_name = 'Configuração do Site'
        verbose_name_plural = 'Configurações do Site'
        ordering = ['chave']
    
    def __str__(self):
        return f"{self.chave}: {self.valor}"