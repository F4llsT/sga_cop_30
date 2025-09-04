from django.db import models
from django.contrib.auth.models import User


class Event(models.Model):
    titulo = models.CharField(max_length=200)
    descricao = models.TextField('Descrição', blank=True, null=True, help_text='Descrição detalhada do evento')
    horario = models.CharField(max_length=50)
    local = models.CharField(max_length=100)
    palestrantes = models.CharField(max_length=200, blank=True)
    tags = models.CharField(max_length=200, blank=True)  # separado por vírgulas
    start_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.titulo

    class Meta:
        verbose_name = 'Evento'
        verbose_name_plural = 'Eventos'
        ordering = ['start_time']

from django.conf import settings
from django.db import models

class UserAgenda(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    event = models.ForeignKey('Event', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.event.titulo}"
