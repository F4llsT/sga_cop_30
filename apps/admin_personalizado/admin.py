# apps/admin_personalizado/admin.py
from django.contrib import admin
from .models import NotificacaoPersonalizada, RedeSocial, Contato, ConfiguracaoSite

@admin.register(NotificacaoPersonalizada)
class NotificacaoPersonalizadaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'status', 'data_criacao', 'data_envio', 'criado_por')
    list_filter = ('status', 'data_criacao')
    search_fields = ('titulo', 'mensagem')
    readonly_fields = ('status', 'data_criacao', 'data_envio', 'criado_por')
    actions = ['enviar_notificacoes']
    
    def save_model(self, request, obj, form, change):
        if not change:  # Se for uma nova notificação
            obj.criado_por = request.user
        super().save_model(request, obj, form, change)
    
    def enviar_notificacoes(self, request, queryset):
        for notificacao in queryset:
            if notificacao.status == 'pendente':
                sucesso, mensagem = notificacao.enviar_notificacoes()
                if sucesso:
                    self.message_user(request, f"✅ {mensagem}", level='success')
                else:
                    self.message_user(request, f"❌ {mensagem}", level='error')
            else:
                self.message_user(request, f"⚠️ Notificação '{notificacao.titulo}' já foi enviada.", level='warning')
    enviar_notificacoes.short_description = "Enviar notificações selecionadas"


@admin.register(RedeSocial)
class RedeSocialAdmin(admin.ModelAdmin):
    list_display = ('nome', 'url', 'icone', 'ativo', 'ordem')
    list_filter = ('ativo',)
    search_fields = ('nome', 'url')
    list_editable = ('ativo', 'ordem')
    ordering = ('ordem', 'nome')


@admin.register(Contato)
class ContatoAdmin(admin.ModelAdmin):
    list_display = ('tipo_contato', 'valor', 'icone', 'ativo', 'ordem')
    list_filter = ('ativo', 'tipo_contato')
    search_fields = ('tipo_contato', 'valor')
    list_editable = ('ativo', 'ordem')
    ordering = ('ordem', 'tipo_contato')


@admin.register(ConfiguracaoSite)
class ConfiguracaoSiteAdmin(admin.ModelAdmin):
    list_display = ('chave', 'valor', 'descricao')
    search_fields = ('chave', 'descricao')
    list_filter = ('chave',)