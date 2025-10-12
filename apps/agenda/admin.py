from django.contrib import admin
from django.utils import timezone 
from django.utils.html import format_html
from .models import Event, UserAgenda 

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    
    # list_display com 'titulo' na frente para garantir que o botão Modificar funcione
    list_display = (
        'titulo', 'local', 'start_time', 'end_time', 'importante', 'is_past_event', 'action_buttons'
    )
    
    list_filter = ('importante', 'local', 'tags', 'start_time')
    search_fields = ('titulo', 'descricao', 'palestrantes', 'tags')
    ordering = ('start_time',)
    list_editable = ('importante',)
    actions = ['marcar_importante', 'desmarcar_importante']

    # Configurações de Formulário
    fieldsets = (
        (None, {
            'fields': ('titulo', 'descricao', 'importante')
        }),
        ('Detalhes do Evento', {
            'fields': ('horario', 'local', 'palestrantes', 'tags', 'start_time', 'end_time')
        }),
        ('Localização', {
            'fields': ('latitude', 'longitude'),
            'classes': ('collapse',),
        }),
    )

    # Templates Customizados
    change_list_template = "admin/agenda/event/dashboard.html"
    change_form_template = "admin/agenda/event/custom_change_form.html" 

    # MÉTODO: Cria o botão de Modificar (USANDO CLASSE CSS LIMPA)
    def action_buttons(self, obj):
        url = f"/admin/agenda/event/{obj.pk}/change/"
        
        # Usa a classe CSS 'btn-admin-action' definida no dashboard.html
        return format_html(
            '<a class="btn-admin-action" href="{}">Modificar</a>',
            url
        )
    action_buttons.short_description = 'AÇÕES' 

    # Método para fornecer dados para o dashboard.html
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        
        extra_context['dashboard_events'] = Event.all_objects.filter(
            importante=True,
            end_time__gte=timezone.now()
        ).order_by('start_time')[:4]
        
        return super().changelist_view(request, extra_context=extra_context)

    # Ações Personalizadas
    @admin.action(description="Marcar eventos selecionados como importantes")
    def marcar_importante(self, request, queryset):
        queryset.update(importante=True)

    @admin.action(description="Desmarcar eventos selecionados como importantes")
    def desmarcar_importante(self, request, queryset):
        queryset.update(importante=False)

    # Coluna customizada na lista
    def is_past_event(self, obj):
        return obj.is_past_event
    is_past_event.boolean = True
    is_past_event.short_description = "Evento já passou?"

@admin.register(UserAgenda)
class UserAgendaAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'added_at')
    list_filter = ('user', 'added_at')
    search_fields = ('user__email', 'event__titulo')
    ordering = ('-added_at',)