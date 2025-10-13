# apps/admin_personalizado/admin.py
from django.contrib import admin
from .models import NotificacaoPersonalizada

@admin.register(NotificacaoPersonalizada)
class NotificacaoPersonalizadaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'status', 'data_criacao', 'data_envio')
    list_filter = ('status',)
    search_fields = ('titulo', 'mensagem')
    readonly_fields = ('status', 'data_criacao', 'data_envio', 'criado_por')
    
    def save_model(self, request, obj, form, change):
        if not change:  # Se for uma nova notificação
            obj.criado_por = request.user
        super().save_model(request, obj, form, change)