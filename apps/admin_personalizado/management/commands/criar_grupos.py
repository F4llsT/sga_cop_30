from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Cria os grupos de usuários e permissões iniciais'

    def handle(self, *args, **options):
        # Obtém ou cria os grupos
        comum, _ = Group.objects.get_or_create(name='Usuário Comum')
        eventos, _ = Group.objects.get_or_create(name='Usuário-Eventos')
        gerente, _ = Group.objects.get_or_create(name='Usuário-Gerente')
        
        # O superusuário é criado pelo comando createsuperuser do Django
        
        self.stdout.write(self.style.SUCCESS('Grupos criados com sucesso!'))