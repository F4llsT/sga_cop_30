from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, View, TemplateView
)
from django.db.models import Q
from django.shortcuts import redirect
from .models import Aviso
from django.utils.translation import gettext_lazy as _

class AvisoMixin(LoginRequiredMixin, UserPassesTestMixin):
    model = Aviso
    fields = ['titulo', 'mensagem', 'nivel', 'data_expiracao', 'fixo_no_topo', 'ativo']
    success_url = reverse_lazy('notificacoes:lista_avisos')

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        form.instance.criado_por = self.request.user
        messages.success(self.request, _("Aviso salvo com sucesso!"))
        return super().form_valid(form)

class ListaAvisosView(LoginRequiredMixin, ListView):
    model = Aviso
    template_name = 'notificacoes/lista_avisos.html'
    context_object_name = 'avisos'
    paginate_by = 10
    
    def get_queryset(self):
        # Mostrar apenas avisos ativos ou fixos no topo
        return Aviso.objects.filter(
            Q(ativo=True) | Q(fixo_no_topo=True)
        ).order_by('-fixo_no_topo', '-data_criacao')

class CriarAvisoView(AvisoMixin, CreateView):
    template_name = 'notificacoes/form_aviso.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = _('Novo Aviso')
        return context

class EditarAvisoView(AvisoMixin, UpdateView):
    template_name = 'notificacoes/form_aviso.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo_pagina'] = _('Editar Aviso')
        return context

class ExcluirAvisoView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Aviso
    success_url = reverse_lazy('notificacoes:lista_avisos')
    
    def test_func(self):
        return self.request.user.is_staff
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, _("Aviso excluído com sucesso!"))
        return super().delete(request, *args, **kwargs)

class ToggleAvisoStatusView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_staff
    
    def post(self, request, *args, **kwargs):
        from django.shortcuts import get_object_or_404
        aviso = get_object_or_404(Aviso, pk=kwargs['pk'])
        aviso.ativo = not aviso.ativo
        aviso.save()
        
        status = _("ativado") if aviso.ativo else _("desativado")
        messages.success(request, _(f"Aviso {status} com sucesso!"))
        return redirect('notificacoes:lista_avisos')


class ArquivoAvisosView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Aviso
    template_name = 'notificacoes/arquivo_avisos.html'
    context_object_name = 'avisos'
    paginate_by = 15
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_queryset(self):
        # Mostrar avisos inativos ou expirados
        from django.utils import timezone
        return Aviso.objects.filter(
            Q(ativo=False) | 
            Q(data_expiracao__lt=timezone.now()) |
            (Q(ativo=True) & Q(data_expiracao__isnull=False) & Q(data_expiracao__lt=timezone.now()))
        ).order_by('-data_criacao')
