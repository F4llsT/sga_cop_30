from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class UsuarioModelTest(TestCase):
    def setUp(self):
        """Configuração inicial para os testes"""
        self.user_data = {
            'email': 'usuario@teste.com',
            'nome': 'Usuário Teste',
            'password': 'senha123',
        }
        
        self.superuser_data = {
            'email': 'admin@teste.com',
            'nome': 'Admin Teste',
            'password': 'admin123',
        }

    def test_criar_usuario_comum(self):
        """Testa a criação de um usuário comum"""
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.nome, self.user_data['nome'])
        self.assertTrue(user.check_password(self.user_data['password']))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)
        
    def test_criar_superusuario(self):
        """Testa a criação de um superusuário"""
        admin = User.objects.create_superuser(**self.superuser_data)
        
        self.assertEqual(admin.email, self.superuser_data['email'])
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_active)
        
    def test_email_obrigatorio(self):
        """Verifica se o email é obrigatório"""
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email='',
                nome='Sem Email',
                password='test123'
            )
            
    def test_nome_obrigatorio(self):
        """Verifica se o nome é obrigatório"""
        user = User(
            email='semnome@teste.com',
            nome='',
            password='test123'
        )
        with self.assertRaises(ValidationError):
            user.full_clean()  # Validação completa do modelo
            
    def test_metodo_str(self):
        """Testa o método __str__ do modelo"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), user.email)  # O método __str__ retorna apenas o email