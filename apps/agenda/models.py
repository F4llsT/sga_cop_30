from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

class EventManager(models.Manager):
    def get_queryset(self):
        # Filtra eventos que ainda não aconteceram ou aconteceram nas últimas 10 horas
        ten_hours_ago = timezone.now() - timedelta(hours=10)
        return super().get_queryset().filter(
            models.Q(start_time__isnull=True) |  # Inclui eventos sem horário definido
            models.Q(start_time__gte=ten_hours_ago)  # Inclui eventos das últimas 10 horas
        )


class Event(models.Model):
    titulo = models.CharField(max_length=200)
    descricao = models.TextField('Descrição', blank=True, null=True, help_text='Descrição detalhada do evento')
    horario = models.CharField(max_length=50)
    local = models.CharField(max_length=100)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    palestrantes = models.CharField(max_length=200, blank=True)
    tags = models.CharField(max_length=200, blank=True)  # separado por vírgulas
    start_time = models.DateTimeField('Data e Hora do Evento', null=True, blank=True)
    end_time = models.DateTimeField('Data e Hora de Término', null=True, blank=True)
    created_at = models.DateTimeField('Criado em', auto_now_add=True)

    # Novo campo
    importante = models.BooleanField(default=False, help_text="Marque se este evento é importante")

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


class UserAgenda(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    event = models.ForeignKey("agenda.Event", on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'event')
        verbose_name = 'Agenda do Usuário'
        verbose_name_plural = 'Agendas dos Usuários'
    
    def __str__(self):
        return f"{self.user} - {self.event.titulo}"
