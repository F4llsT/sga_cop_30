from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.utils.translation import gettext_lazy as _

class UsuarioManager(BaseUserManager):
    """Gerenciador personalizado para o modelo de usuário."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Cria e salva um usuário com o email e senha fornecidos."""
        if not email:
            raise ValueError('O email é obrigatório')
        email = self.normalize_email(email)
        
        # Define o papel padrão como USUARIO se não for especificado
        if 'role' not in extra_fields:
            extra_fields['role'] = Usuario.Role.USUARIO
            
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        
        # Adiciona ao grupo correspondente ao papel
        if user.role == Usuario.Role.EVENTOS:
            grupo_eventos, _ = Group.objects.get_or_create(name='Usuário de Eventos')
            user.groups.add(grupo_eventos)
        elif user.role == Usuario.Role.GERENTE:
            grupo_gerente, _ = Group.objects.get_or_create(name='Usuário Gerente')
            user.groups.add(grupo_gerente)
            
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Cria e salva um superusuário com o email e senha fornecidos."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', Usuario.Role.SUPERUSER)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superusuário deve ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superusuário deve ter is_superuser=True.')

        user = self.create_user(email, password, **extra_fields)
        
        # Adiciona ao grupo de superusuários
        grupo_superuser, _ = Group.objects.get_or_create(name='Superusuário')
        user.groups.add(grupo_superuser)
        
        return user


class Usuario(AbstractUser):
    """Modelo de usuário personalizado que usa email como identificador."""
    
    class Role(models.TextChoices):
        USUARIO = 'USUARIO', _('Usuário Comum')
        EVENTOS = 'EVENTOS', _('Usuário de Eventos')
        GERENTE = 'GERENTE', _('Usuário Gerente')
        SUPERUSER = 'SUPERUSER', _('Superusuário')
    
    username = None
    email = models.EmailField(_('endereço de email'), unique=True)
    nome = models.CharField(_('nome completo'), max_length=150, blank=False, null=False)
    data_cadastro = models.DateTimeField(_('data de cadastro'), auto_now_add=True)
    role = models.CharField(
        _('papel'),
        max_length=20,
        choices=Role.choices,
        default=Role.USUARIO,
        help_text=_('Nível de acesso do usuário no sistema')
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome']  # Adiciona 'nome' aos campos obrigatórios
    
    objects = UsuarioManager()
    
    def __str__(self):
        return self.email
    
    @property
    def is_usuario_comum(self):
        return self.role == self.Role.USUARIO
    
    @property
    def is_usuario_eventos(self):
        return self.role == self.Role.EVENTOS
    
    @property
    def is_gerente(self):
        return self.role == self.Role.GERENTE
    
    @property
    def is_superusuario(self):
        return self.role == self.Role.SUPERUSER or self.is_superuser
    
    def has_perm(self, perm, obj=None):
        """Verifica se o usuário tem a permissão especificada."""
        # Superusuários têm todas as permissões
        if self.is_superusuario:
            return True
            
        # Gerentes têm permissões específicas
        if self.is_gerente:
            # Permite visualização, mas não modificação de usuários
            if perm in ['usuarios.view_usuario', 'auth.view_group']:
                return True
            # Permite gerenciar eventos
            if perm.startswith('eventos.'):
                return True
        
        # Usuários de eventos podem gerenciar eventos
        if self.is_usuario_eventos and perm.startswith('eventos.'):
            return True
            
        return super().has_perm(perm, obj)
    
    def save(self, *args, **kwargs):
        """Sobrescreve o método save para garantir consistência dos grupos."""
        is_new = self.pk is None
        old_role = None
        
        if not is_new:
            old_instance = Usuario.objects.get(pk=self.pk)
            old_role = old_instance.role
        
        super().save(*args, **kwargs)
        
        # Atualiza os grupos quando o papel é alterado
        if not is_new and old_role != self.role:
            self.groups.clear()
            
            if self.role == self.Role.EVENTOS:
                grupo, _ = Group.objects.get_or_create(name='Usuário de Eventos')
                self.groups.add(grupo)
            elif self.role == self.Role.GERENTE:
                grupo, _ = Group.objects.get_or_create(name='Usuário Gerente')
                self.groups.add(grupo)
            elif self.role == self.Role.SUPERUSER:
                grupo, _ = Group.objects.get_or_create(name='Superusuário')
                self.groups.add(grupo)
    
    class Meta:
        verbose_name = _('usuário')
        verbose_name_plural = _('usuários')
        permissions = [
            ('pode_gerenciar_eventos', 'Pode gerenciar eventos'),
            ('pode_visualizar_usuarios', 'Pode visualizar usuários'),
            ('pode_gerenciar_usuarios', 'Pode gerenciar usuários'),
        ]


class Perfil(models.Model):
    """Perfil adicional para informações extras do usuário."""
    
    class Genero(models.TextChoices):
        MASCULINO = 'M', _('Masculino')
        FEMININO = 'F', _('Feminino')
        OUTRO = 'O', _('Outro')
        NAO_INFORMAR = 'N', _('Prefiro não informar')
    
    usuario = models.OneToOneField(
        Usuario, 
        on_delete=models.CASCADE,
        related_name='perfil'
    )
    genero = models.CharField(
        _('gênero'),
        max_length=1,
        choices=Genero.choices,
        default=Genero.NAO_INFORMAR,
        blank=True,
        null=True
    )
    cep = models.CharField(
        _('CEP'),
        max_length=9,
        blank=True,
        null=True,
        help_text=_('Formato: 00000-000')
    )
    logradouro = models.CharField(
        _('logradouro'),
        max_length=255,
        blank=True,
        null=True,
        help_text=_('Nome da rua, avenida, etc.')
    )
    numero = models.CharField(
        _('número'),
        max_length=20,
        blank=True,
        null=True
    )
    complemento = models.CharField(
        _('complemento'),
        max_length=100,
        blank=True,
        null=True
    )
    bairro = models.CharField(
        _('bairro'),
        max_length=100,
        blank=True,
        null=True
    )
    cidade = models.CharField(
        _('cidade'),
        max_length=100,
        blank=True,
        null=True
    )
    estado = models.CharField(
        _('estado'),
        max_length=2,
        blank=True,
        null=True,
        help_text=_('Sigla do estado (ex: SP, RJ)')
    )
    telefone = models.CharField(
        _('telefone'),
        max_length=20,
        blank=True,
        null=True,
        help_text=_('Formato: (00) 00000-0000')
    )
    telefone_whatsapp = models.BooleanField(
        _('WhatsApp?'),
        default=False,
        help_text=_('Este número tem WhatsApp?')
    )
    data_nascimento = models.DateField(
        _('data de nascimento'),
        blank=True,
        null=True
    )
    foto_perfil = models.ImageField(
        _('foto de perfil'),
        upload_to='perfis/',
        blank=True,
        null=True
    )
    
    def __str__(self):
        return f'Perfil de {self.usuario.email}'
    
    class Meta:
        verbose_name = _('perfil')
        verbose_name_plural = _('perfis')
