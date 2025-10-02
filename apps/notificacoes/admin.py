from django.contrib import admin
from .models import Aviso
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _


@admin.register(Aviso)
class AvisoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'nivel_formatado', 'data_criacao', 'data_expiracao', 
                   'fixo_no_topo', 'ativo', 'esta_expirado')
    list_filter = ('nivel', 'fixo_no_topo', 'ativo')
    search_fields = ('titulo', 'mensagem')
    date_hierarchy = 'data_criacao'
    readonly_fields = ('criado_por', 'data_criacao')
    fieldsets = (
        (None, {
            'fields': ('titulo', 'mensagem', 'nivel')
        }),
        (_('Configurações'), {
            'fields': ('data_expiracao', 'fixo_no_topo', 'ativo')
        }),
        (_('Metadados'), {
            'fields': ('criado_por', 'data_criacao'),
            'classes': ('collapse',)
        }),
    )

    def nivel_formatado(self, obj):
        niveis = {
            'info': ('info', 'Informação'),
            'alerta': ('warning', 'Alerta'),
            'critico': ('danger', 'Crítico')
        }
        classe, texto = niveis.get(obj.nivel, ('secondary', 'Desconhecido'))
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            classe, texto
        )
    nivel_formatado.short_description = _('Nível')
    nivel_formatado.admin_order_field = 'nivel'

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Se for uma nova instância
            obj.criado_por = request.user
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('criado_por')

    def esta_expirado(self, obj):
        return obj.esta_expirado
    esta_expirado.boolean = True
    esta_expirado.short_description = _('Expirado')
