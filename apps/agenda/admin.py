from django.contrib import admin
from .models import Event, UserAgenda

# Register your models here.

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'horario', 'local', 'start_time')
    list_filter = ('local', 'tags')
    search_fields = ('titulo', 'palestrantes', 'tags', 'descricao')
    ordering = ('start_time',)
    fieldsets = (
        (None, {
            'fields': ('titulo', 'descricao')
        }),
        ('Detalhes do Evento', {
            'fields': ('horario', 'local', 'palestrantes', 'tags', 'start_time')
        }),
    )

@admin.register(UserAgenda)
class UserAgendaAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'added_at')
    list_filter = ('user', 'added_at')
    search_fields = ('user__email', 'event__titulo')
    ordering = ('-added_at',)
