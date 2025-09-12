from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _

class UsuarioManager(BaseUserManager):
    """Gerenciador personalizado para o modelo de usuário."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Cria e salva um usuário com o email e senha fornecidos."""
        if not email:
            raise ValueError('O email é obrigatório')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Cria e salva um superusuário com o email e senha fornecidos."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superusuário deve ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superusuário deve ter is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractUser):
    """Modelo de usuário personalizado que usa email como identificador."""
    
    username = None
    email = models.EmailField(_('endereço de email'), unique=True)
    nome = models.CharField(_('nome completo'), max_length=150, blank=False, null=False)  # Campo obrigatório
    data_cadastro = models.DateTimeField(_('data de cadastro'), auto_now_add=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome']  # Adiciona 'nome' aos campos obrigatórios
    
    objects = UsuarioManager()
    
    def __str__(self):
        return self.email
    
    class Meta:
        verbose_name = _('usuário')
        verbose_name_plural = _('usuários')


class Perfil(models.Model):
    """Perfil adicional para informações extras do usuário."""
    usuario = models.OneToOneField(
        Usuario, 
        on_delete=models.CASCADE,
        related_name='perfil'
    )
    telefone = models.CharField(max_length=20, blank=True, null=True)
    data_nascimento = models.DateField(blank=True, null=True)
    foto_perfil = models.ImageField(upload_to='perfis/', blank=True, null=True)
    
    def __str__(self):
        return f'Perfil de {self.usuario.email}'
    
    class Meta:
        verbose_name = _('perfil')
        verbose_name_plural = _('perfis')
