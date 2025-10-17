from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

# Obter o modelo de usuário ativo
User = get_user_model()

class EventManager(models.Manager):
    def get_queryset(self):
        """Filtra apenas eventos ativos (últimas 10 horas ou sem horário definido)"""
        ten_hours_ago = timezone.now() - timedelta(hours=10)
        return super().get_queryset().filter(
            models.Q(start_time__isnull=True) |  # Inclui eventos sem horário definido
            models.Q(start_time__gte=ten_hours_ago)  # Inclui eventos das últimas 10 horas
        )

class Event(models.Model):
    titulo = models.CharField(max_length=200, verbose_name='Título')
    descricao = models.TextField(blank=True, null=True, verbose_name='Descrição')
    local = models.CharField(max_length=200, verbose_name='Local')
    palestrante = models.CharField(max_length=200, blank=True, null=True, verbose_name='Palestrante')
    start_time = models.DateTimeField(verbose_name='Data e Hora de Início')
    end_time = models.DateTimeField(verbose_name='Data e Hora de Término')
    tags = models.CharField(max_length=100, default='sustentabilidade', verbose_name='Tema')
    importante = models.BooleanField(default=False, verbose_name='Evento Importante')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name='Criado por',
        related_name='eventos_criados'
    )
    
    # Gerenciadores
    objects = EventManager()
    all_objects = models.Manager()  # Gerenciador para acessar todos os registros

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'
        ordering = ['start_time']

    @property
    def is_past_event(self):
        """Retorna True se o evento já passou há mais de 10 horas."""
        if not self.start_time:
            return False
        return self.start_time < (timezone.now() - timedelta(hours=10))