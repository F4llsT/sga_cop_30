from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
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
    data_expiracao = models.DateTimeField('Data de Expiração',null=True,blank=True,help_text='Data em que a notificação será considerada expirada')
    class Meta:
        ordering = ['-criada_em']
        verbose_name = 'Notificação'
        verbose_name_plural = 'Notificações'

    def save(self, *args, **kwargs):
        # Set default expiration to 30 days from creation if not set
        if not self.pk and not self.data_expiracao:
            self.data_expiracao = timezone.now() + timedelta(days=30)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.titulo} - {self.usuario.nome}"
    
    def marcar_como_lida(self):
        if not self.lida:
            self.lida = True
            self.lida_em = timezone.now()
            self.save()

# apps/notificacoes/models.py
    def save(self, *args, **kwargs):
        # Se for uma nova notificação
        if not self.pk:
            # Define a expiração padrão para 10 dias
            self.data_expiracao = timezone.now() + timezone.timedelta(days=10)
        
        # Se a notificação for marcada como lida, atualiza a expiração para 1 hora
        if self.lida and not self.lida_em:
            self.lida_em = timezone.now()
            self.data_expiracao = timezone.now() + timezone.timedelta(hours=1)
        
        super().save(*args, **kwargs)


    @property
    def expirada(self):
        """Verifica se a notificação expirou"""
        if self.data_expiracao:
            return timezone.now() > self.data_expiracao
        return False
    
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


class Aviso(models.Model):
    NIVEL_IMPORTANCIA = [
        ('info', 'Informativo'),
        ('alerta', 'Alerta'),
        ('critico', 'Crítico'),
    ]
    
    titulo = models.CharField(_('título'), max_length=200)
    mensagem = models.TextField(_('mensagem'))
    nivel = models.CharField(
        _('nível de importância'),
        max_length=10, 
        choices=NIVEL_IMPORTANCIA, 
        default='info'
    )
    data_criacao = models.DateTimeField(_('data de criação'), auto_now_add=True)
    data_expiracao = models.DateTimeField(_('data de expiração'), null=True, blank=True)
    fixo_no_topo = models.BooleanField(_('fixo no topo'), default=False)
    ativo = models.BooleanField(_('ativo'), default=True)
    criado_por = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='avisos_criados',
        verbose_name=_('criado por')
    )
    
    class Meta:
        verbose_name = _('Aviso')
        verbose_name_plural = _('Avisos')
        ordering = ['-fixo_no_topo', '-data_criacao']
    
    def __str__(self):
        return self.titulo
    
    @property
    def esta_expirado(self):
        if self.data_expiracao:
            return timezone.now() > self.data_expiracao
        return False
    
    @property
    def esta_visivel(self):
        return self.ativo and not self.esta_expirado
    
    @property
    def classe_css(self):
        return {
            'info': 'info',
            'alerta': 'warning',
            'critico': 'danger'
        }.get(self.nivel, 'info')
    
    @property
    def icone(self):
        return {
            'info': 'info-circle',
            'alerta': 'exclamation-triangle',
            'critico': 'exclamation-circle'
        }.get(self.nivel, 'info')
