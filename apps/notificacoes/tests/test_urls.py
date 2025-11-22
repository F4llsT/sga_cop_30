from django.test import TestCase
from django.urls import reverse, resolve
from .. import urls
from ..views_avisos import (
    ListaAvisosView, CriarAvisoView, EditarAvisoView,
    ExcluirAvisoView, ToggleAvisoStatusView, ArquivoAvisosView
)

class UrlsTest(TestCase):
    def test_lista_avisos_url_resolves(self):
        """Testa a URL da lista de avisos"""
        url = reverse('notificacoes:lista_avisos')
        self.assertEqual(resolve(url).func.view_class, ListaAvisosView)
    
    def test_criar_aviso_url_resolves(self):
        """Testa a URL de criação de aviso"""
        url = reverse('notificacoes:criar_aviso')
        self.assertEqual(resolve(url).func.view_class, CriarAvisoView)
    
    def test_editar_aviso_url_resolves(self):
        """Testa a URL de edição de aviso"""
        url = reverse('notificacoes:editar_aviso', args=[1])
        self.assertEqual(resolve(url).func.view_class, EditarAvisoView)
    
    def test_excluir_aviso_url_resolves(self):
        """Testa a URL de exclusão de aviso"""
        url = reverse('notificacoes:excluir_aviso', args=[1])
        self.assertEqual(resolve(url).func.view_class, ExcluirAvisoView)
    
    def test_toggle_aviso_url_resolves(self):
        """Testa a URL de alternância de status de aviso"""
        url = reverse('notificacoes:toggle_aviso', args=[1])
        self.assertEqual(resolve(url).func.view_class, ToggleAvisoStatusView)
    
    def test_arquivo_avisos_url_resolves(self):
        """Testa a URL do arquivo de avisos"""
        url = reverse('notificacoes:arquivo_avisos')
        self.assertEqual(resolve(url).func.view_class, ArquivoAvisosView)
