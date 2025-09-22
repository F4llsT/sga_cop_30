# apps/passefacil/admin.py
from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.utils.html import format_html
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from .models import PasseFacil, ValidacaoQRCode
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from .models import PasseFacil, ValidacaoQRCode
from .admin_views import validar_qr_code

class PasseFacilAdmin(admin.ModelAdmin):
    list_display = ('user', 'codigo', 'ultima_validacao', 'status_validacao', 'acoes')
    list_filter = ('ativo',)
    search_fields = ('user__username', 'user__email', 'codigo')
    change_list_template = 'admin/passefacil/change_list.html'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'validar-qr-code/',
                self.admin_site.admin_view(validar_qr_code),
                name='passefacil_validar_qr_code',
            ),
        ]
        return custom_urls + urls
    
    def ultima_validacao(self, obj):
        ultima = obj.validacoes.order_by('-data_validacao').first()
        return ultima.data_validacao.strftime('%d/%m/%Y %H:%M') if ultima else 'Nunca validado'
    ultima_validacao.short_description = 'Última Validação'
    
    def status_validacao(self, obj):
        ultima = obj.validacoes.order_by('-data_validacao').first()
        if not ultima:
            return format_html('<span class="badge bg-secondary">Nunca validado</span>')
        if ultima.valido:
            return format_html('<span class="badge bg-success">Válido</span>')
        return format_html('<span class="badge bg-danger">Inválido</span>')
    status_validacao.short_description = 'Status'
    
    def acoes(self, obj):
        return format_html(
            '<a href="{}" class="button" title="Editar"><i class="fas fa-edit"></i></a>',
            f'/admin/passefacil/passefacil/{obj.id}/change/'
        )
    acoes.short_description = 'Ações'
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        
        # Estatísticas
        hoje = timezone.now().date()
        validacoes_hoje = ValidacaoQRCode.objects.filter(
            data_validacao__date=hoje
        )
        
        # Lista de passes com informações de validação
        passes = PasseFacil.objects.prefetch_related('validacoes').all()
        
        extra_context.update({
            'total_validacoes_hoje': validacoes_hoje.count(),
            'validacoes_validas': validacoes_hoje.filter(valido=True).count(),
            'validacoes_invalidas': validacoes_hoje.filter(valido=False).count(),
            'ultimas_validacoes': validacoes_hoje.select_related('passe_facil__user').order_by('-data_validacao')[:10],
            'total_passes': passes.count(),
            'passes_ativos': passes.filter(ativo=True).count(),
            'passes_inativos': passes.filter(ativo=False).count(),
        })
        
        return super().changelist_view(request, extra_context=extra_context)

    def has_add_permission(self, request):
        return False

@admin.register(ValidacaoQRCode)
class ValidacaoQRCodeAdmin(admin.ModelAdmin):
    list_display = ('passe_facil', 'data_validacao', 'valido', 'ip_address')
    list_filter = ('valido', 'data_validacao')
    search_fields = ('passe_facil__user__username', 'passe_facil__codigo', 'ip_address')
    readonly_fields = ('data_validacao', 'ip_address')
    
    def has_add_permission(self, request):
        return False

admin.site.register(PasseFacil, PasseFacilAdmin)