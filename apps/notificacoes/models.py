from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.agenda.models import Event

User = get_user_model()

class Notificacao(models.Model):
    TIPO_CHOICES = [
        ('info', 'Informação'),
        ('success', 'Sucesso'),
        ('warning', 'Aviso'),
        ('error', 'Erro'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificacoes')
    titulo = models.CharField(max_length=200)
    mensagem = models.TextField()
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='info')
    lida = models.BooleanField(default=False)
    criada_em = models.DateTimeField(auto_now_add=True)
    lida_em = models.DateTimeField(null=True, blank=True)
    evento = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True, related_name='notificacoes_evento')
    
    class Meta:
        ordering = ['-criada_em']
        verbose_name = 'Notificação'
        verbose_name_plural = 'Notificações'
    
    def __str__(self):
        return f"{self.titulo} - {self.usuario.nome}"
    
    def marcar_como_lida(self):
        if not self.lida:
            self.lida = True
            self.lida_em = timezone.now()
            self.save()
    
    @property
    def tempo_decorrido(self):
        """Retorna o tempo decorrido desde a criação da notificação"""
        agora = timezone.now()
        diferenca = agora - self.criada_em
        
        if diferenca.days > 0:
            return f"há {diferenca.days} dia{'s' if diferenca.days > 1 else ''}"
        elif diferenca.seconds > 3600:
            horas = diferenca.seconds // 3600
            return f"há {horas} hora{'s' if horas > 1 else ''}"
        elif diferenca.seconds > 60:
            minutos = diferenca.seconds // 60
            return f"há {minutos} minuto{'s' if minutos > 1 else ''}"
        else:
            return "agora mesmo"
