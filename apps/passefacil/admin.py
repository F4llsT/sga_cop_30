# apps/passefacil/admin.py
from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.utils.html import format_html
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from .models import PasseFacil, ValidacaoQRCode
from django.db.models import Count, Q
from django.contrib import messages

@admin.register(ValidacaoQRCode)
class ValidacaoQRCodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'passe_facil', 'codigo', 'valido', 'data_validacao', 'ip_address')
    list_filter = ('valido', 'data_validacao')
    search_fields = ('passe_facil__user__username', 'codigo', 'ip_address')
    date_hierarchy = 'data_validacao'

@admin.register(PasseFacil)
class PasseFacilAdmin(admin.ModelAdmin):
    list_display = ('user', 'codigo', 'data_atualizacao', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('user__username', 'user__email', 'codigo')
    change_list_template = 'admin/passefacil/dashboard.html'
    
    def has_add_permission(self, request):
        return False
    
    def changelist_view(self, request, extra_context=None):
        # Adicione aqui a lógica do seu painel
        if extra_context is None:
            extra_context = {}
            
        # Sua lógica de dashboard aqui
        hoje = timezone.now().date()
        validacoes_hoje = ValidacaoQRCode.objects.filter(
            data_validacao__date=hoje
        )
        
        extra_context.update({
            'total_validacoes_hoje': validacoes_hoje.count(),
            'validacoes_validas': validacoes_hoje.filter(valido=True).count(),
            'validacoes_invalidas': validacoes_hoje.filter(valido=False).count(),
            'ultimas_validacoes': validacoes_hoje.select_related('passe_facil__user')[:10]
        })
        
        return super().changelist_view(request, extra_context=extra_context)