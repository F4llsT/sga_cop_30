# apps/passefacil/admin.py
from django.contrib import admin
from .models import PasseFacil, ValidacaoQRCode

@admin.register(PasseFacil)
class PasseFacilAdmin(admin.ModelAdmin):
    list_display = ('user', 'codigo', 'data_atualizacao', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('user__username', 'user__email', 'codigo')

@admin.register(ValidacaoQRCode)
class ValidacaoQRCodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'passe_facil', 'codigo', 'valido', 'data_validacao', 'ip_address')
    list_filter = ('valido', 'data_validacao')
    search_fields = ('passe_facil__user__username', 'codigo', 'ip_address')
    date_hierarchy = 'data_validacao'