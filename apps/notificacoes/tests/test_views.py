from django.test import TestCase, RequestFactory
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.messages import get_messages
from django.contrib.messages.storage.fallback import FallbackStorage
from django.http import Http404

from ..models import Aviso
from ..views_avisos import (
    ListaAvisosView, CriarAvisoView, EditarAvisoView, 
    ExcluirAvisoView, ToggleAvisoStatusView, ArquivoAvisosView
)

User = get_user_model()

class AvisoViewTest(TestCase):
    def setUp(self):
        # Configuração inicial para os testes
        self.factory = RequestFactory()
        
        # Cria um usuário administrador
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123',
            nome='Admin User'
        )
        
        # Cria um usuário normal (não administrador)
        self.user = User.objects.create_user(
            email='user@example.com',
            password='testpass123',
            nome='Test User',
            role=User.Role.USUARIO
        )
        
        # Cria alguns avisos para teste
        self.aviso1 = Aviso.objects.create(
            titulo='Aviso 1',
            mensagem='Mensagem do aviso 1',
            nivel='info',
            criado_por=self.admin_user,
            fixo_no_topo=True,
            ativo=True
        )
        
        self.aviso2 = Aviso.objects.create(
            titulo='Aviso 2',
            mensagem='Mensagem do aviso 2',
            nivel='alerta',
            criado_por=self.admin_user,
            fixo_no_topo=False,
            ativo=True,
            data_expiracao=timezone.now() + timezone.timedelta(days=1)
        )
        
        # URLS
        self.lista_url = reverse('notificacoes:lista_avisos')
        self.criar_url = reverse('notificacoes:criar_aviso')
        self.editar_url = reverse('notificacoes:editar_aviso', args=[self.aviso1.id])
        self.excluir_url = reverse('notificacoes:excluir_aviso', args=[self.aviso1.id])
        self.toggle_url = reverse('notificacoes:toggle_aviso', args=[self.aviso1.id])
        self.arquivo_url = reverse('notificacoes:arquivo_avisos')
    
    def test_lista_avisos_view_get(self):
        """Testa a visualização da lista de avisos"""
        # Usuário não logado é redirecionado para o login
        response = self.client.get(self.lista_url)
        self.assertEqual(response.status_code, 302)
        
        # Usuário logado pode acessar
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.lista_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notificacoes/lista_avisos.html')
        self.assertIn('avisos', response.context)
        
        # Verifica se apenas avisos ativos ou fixos são retornados
        avisos = response.context['avisos']
        self.assertEqual(avisos.count(), 2)
        self.assertTrue(all(aviso.ativo or aviso.fixo_no_topo for aviso in avisos))
    
    def test_criar_aviso_view_get(self):
        """Testa o acesso ao formulário de criação de aviso"""
        # Usuário não logado é redirecionado
        response = self.client.get(self.criar_url)
        self.assertEqual(response.status_code, 302)
        
        # Usuário normal não tem permissão
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.criar_url)
        self.assertEqual(response.status_code, 403)  # Forbidden
        
        # Admin tem permissão
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(self.criar_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notificacoes/form_aviso.html')
        self.assertIn('form', response.context)
    
    def test_criar_aviso_view_post(self):
        """Testa a criação de um novo aviso"""
        self.client.login(username='admin', password='adminpass123')
        
        # Dados válidos
        data = {
            'titulo': 'Novo Aviso',
            'mensagem': 'Este é um novo aviso',
            'nivel': 'info',
            'fixo_no_topo': False,
            'ativo': True
        }
        
        response = self.client.post(self.criar_url, data)
        
        # Verifica se redireciona para a lista após salvar
        self.assertRedirects(response, reverse('notificacoes:lista_avisos'))
        
        # Verifica se o aviso foi criado
        self.assertTrue(Aviso.objects.filter(titulo='Novo Aviso').exists())
        
        # Verifica a mensagem de sucesso
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Aviso salvo com sucesso!')
    
    def test_editar_aviso_view_get(self):
        """Testa o acesso ao formulário de edição de aviso"""
        # Usuário não logado é redirecionado
        response = self.client.get(self.editar_url)
        self.assertEqual(response.status_code, 302)
        
        # Usuário normal não tem permissão
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.editar_url)
        self.assertEqual(response.status_code, 403)  # Forbidden
        
        # Admin tem permissão
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(self.editar_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notificacoes/form_aviso.html')
        self.assertIn('form', response.context)
        self.assertEqual(response.context['titulo_pagina'], 'Editar Aviso')
    
    def test_editar_aviso_view_post(self):
        """Testa a edição de um aviso existente"""
        self.client.login(username='admin', password='adminpass123')
        
        # Dados atualizados
        data = {
            'titulo': 'Aviso Atualizado',
            'mensagem': 'Mensagem atualizada',
            'nivel': 'alerta',
            'fixo_no_topo': True,
            'ativo': True
        }
        
        response = self.client.post(self.editar_url, data)
        
        # Verifica se redireciona para a lista após salvar
        self.assertRedirects(response, reverse('notificacoes:lista_avisos'))
        
        # Verifica se o aviso foi atualizado
        aviso_atualizado = Aviso.objects.get(id=self.aviso1.id)
        self.assertEqual(aviso_atualizado.titulo, 'Aviso Atualizado')
        self.assertEqual(aviso_atualizado.mensagem, 'Mensagem atualizada')
        self.assertEqual(aviso_atualizado.nivel, 'alerta')
        self.assertTrue(aviso_atualizado.fixo_no_topo)
        
        # Verifica a mensagem de sucesso
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Aviso salvo com sucesso!')
    
    def test_excluir_aviso_view(self):
        """Testa a exclusão de um aviso"""
        self.client.login(username='admin', password='adminpass123')
        
        # Cria um aviso para ser excluído
        aviso_para_excluir = Aviso.objects.create(
            titulo='Aviso para Excluir',
            mensagem='Este aviso será excluído',
            nivel='info',
            criado_por=self.admin_user
        )
        
        # Verifica se o aviso existe antes da exclusão
        self.assertTrue(Aviso.objects.filter(id=aviso_para_excluir.id).exists())
        
        # Faz a requisição POST para excluir
        response = self.client.post(reverse('notificacoes:excluir_aviso', args=[aviso_para_excluir.id]))
        
        # Verifica se redireciona para a lista após excluir
        self.assertRedirects(response, reverse('notificacoes:lista_avisos'))
        
        # Verifica se o aviso foi excluído
        self.assertFalse(Aviso.objects.filter(id=aviso_para_excluir.id).exists())
        
        # Verifica a mensagem de sucesso
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Aviso excluído com sucesso!')
    
    def test_toggle_aviso_status_view(self):
        """Testa a alternância do status de um aviso (ativo/inativo)"""
        self.client.login(username='admin', password='adminpass123')
        
        # Status inicial do aviso
        status_inicial = self.aviso1.ativo
        
        # Faz a requisição POST para alternar o status
        response = self.client.post(self.toggle_url)
        
        # Verifica se redireciona para a lista
        self.assertRedirects(response, reverse('notificacoes:lista_avisos'))
        
        # Verifica se o status foi alterado
        aviso_atualizado = Aviso.objects.get(id=self.aviso1.id)
        self.assertNotEqual(aviso_atualizado.ativo, status_inicial)
        
        # Verifica a mensagem de sucesso
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertIn('ativado' if not status_inicial else 'desativado', str(messages[0]))
    
    def test_arquivo_avisos_view(self):
        """Testa a visualização do arquivo de avisos (inativos/arquivados)"""
        # Cria um aviso inativo para teste
        aviso_inativo = Aviso.objects.create(
            titulo='Aviso Inativo',
            mensagem='Este aviso está inativo',
            nivel='info',
            criado_por=self.admin_user,
            ativo=False
        )
        
        # Cria um aviso expirado para teste
        aviso_expirado = Aviso.objects.create(
            titulo='Aviso Expirado',
            mensagem='Este aviso expirou',
            nivel='alerta',
            criado_por=self.admin_user,
            ativo=True,
            data_expiracao=timezone.now() - timezone.timedelta(days=1)
        )
        
        # Usuário não logado é redirecionado
        response = self.client.get(self.arquivo_url)
        self.assertEqual(response.status_code, 302)
        
        # Usuário normal não tem permissão
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.arquivo_url)
        self.assertEqual(response.status_code, 403)  # Forbidden
        
        # Admin tem permissão
        self.client.login(username='admin', password='adminpass123')
        response = self.client.get(self.arquivo_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notificacoes/arquivo_avisos.html')
        
        # Verifica se apenas avisos inativos ou expirados são exibidos
        avisos = response.context['avisos']
        self.assertEqual(avisos.count(), 2)  # Deve incluir aviso_inativo e aviso_expirado
        self.assertTrue(all(not aviso.esta_visivel for aviso in avisos))
