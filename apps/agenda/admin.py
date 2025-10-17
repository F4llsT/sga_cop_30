from django.contrib import admin
from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'start_time', 'end_time', 'local', 'palestrante', 'importante')
    list_filter = ('importante', 'tags', 'start_time')
    search_fields = ('titulo', 'descricao', 'local', 'palestrante')
    date_hierarchy = 'start_time'
    ordering = ('-start_time',)
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('titulo', 'descricao', 'tags', 'importante')
        }),
        ('Local e Data', {
            'fields': ('local', 'start_time', 'end_time')
        }),
        ('Palestrante', {
            'fields': ('palestrante',)
        }),
    )