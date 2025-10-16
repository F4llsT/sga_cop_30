from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied

from ..models import Usuario

class PermissionsTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        
        # Criar grupos de permissões
        self.grupo_gerente, _ = Group.objects.get_or_create(name='Gerente')
        self.grupo_eventos, _ = Group.objects.get_or_create(name='Eventos')
        
        # Criar permissões de exemplo
        content_type = ContentType.objects.get_for_model(Usuario)
        self.permission_view = Permission.objects.create(
            codename='view_usuario',
            name='Can view usuario',
            content_type=content_type,
        )
        
        # Criar usuários de teste
        self.superuser = Usuario.objects.create_superuser(
            email='admin@example.com',
            nome='Admin',
            password='admin123',
            role=Usuario.Role.SUPERUSER
        )
        
        self.gerente = Usuario.objects.create_user(
            email='gerente@example.com',
            nome='Gerente',
            password='gerente123',
            role=Usuario.Role.GERENTE
        )
        self.gerente.groups.add(self.grupo_gerente)
        
        self.usuario_eventos = Usuario.objects.create_user(
            email='eventos@example.com',
            nome='Usuário Eventos',
            password='eventos123',
            role=Usuario.Role.EVENTOS
        )
        self.usuario_eventos.groups.add(self.grupo_eventos)
        
        self.usuario_comum = Usuario.objects.create_user(
            email='comum@example.com',
            nome='Usuário Comum',
            password='comum123',
            role=Usuario.Role.USUARIO
        )
    
    def test_superuser_permissions(self):
        """Superusuário deve ter todas as permissões"""
        self.assertTrue(self.superuser.has_perm('usuarios.view_usuario'))
        self.assertTrue(self.superuser.has_perm('usuarios.change_usuario'))
        self.assertTrue(self.superuser.has_perm('eventos.add_evento'))
        self.assertTrue(self.superuser.has_perm('dashboard.view_dashboard'))
    
    def test_gerente_permissions(self):
        """Gerente pode visualizar usuários e gerenciar eventos, mas não modificar usuários"""
        # Deve ter permissão
        self.assertTrue(self.gerente.has_perm('usuarios.view_usuario'))
        self.assertTrue(self.gerente.has_perm('eventos.view_evento'))
        self.assertTrue(self.gerente.has_perm('dashboard.view_dashboard'))
        
        # Não deve ter permissão
        self.assertFalse(self.gerente.has_perm('usuarios.add_usuario'))
        self.assertFalse(self.gerente.has_perm('usuarios.change_usuario'))
        self.assertFalse(self.gerente.has_perm('usuarios.delete_usuario'))
        self.assertFalse(self.gerente.has_perm('auth.add_group'))
    
    def test_usuario_eventos_permissions(self):
        """Usuário de eventos pode acessar dashboard e gerenciar eventos"""
        # Deve ter permissão
        self.assertTrue(self.usuario_eventos.has_perm('eventos.view_evento'))
        self.assertTrue(self.usuario_eventos.has_perm('eventos.add_evento'))
        self.assertTrue(self.usuario_eventos.has_perm('dashboard.view_dashboard'))
        
        # Pode ver o próprio perfil
        self.assertTrue(self.usuario_eventos.has_perm('usuarios.view_perfil', self.usuario_eventos))
        
        # Não deve ter permissão
        self.assertFalse(self.usuario_eventos.has_perm('usuarios.view_usuario'))
        self.assertFalse(self.usuario_eventos.has_perm('auth.view_group'))
        
        # Não pode ver perfil de outros usuários
        self.assertFalse(self.usuario_eventos.has_perm('usuarios.view_perfil', self.gerente))
    
    def test_usuario_comum_permissions(self):
        """Usuário comum não deve ter permissões administrativas"""
        # Não deve ter permissões administrativas
        self.assertFalse(self.usuario_comum.has_perm('usuarios.view_usuario'))
        self.assertFalse(self.usuario_comum.has_perm('eventos.view_evento'))
        self.assertFalse(self.usuario_comum.has_perm('dashboard.view_dashboard'))
        
        # Pode ver o próprio perfil
        self.assertTrue(self.usuario_comum.has_perm('usuarios.view_perfil', self.usuario_comum))
