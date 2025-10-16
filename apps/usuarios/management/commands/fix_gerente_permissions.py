from django.core.management.base import BaseCommand
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from ...models import Usuario

class Command(BaseCommand):
    help = 'Corrige as permissões para usuários gerentes'

    def handle(self, *args, **options):
        with transaction.atomic():
            # Atualizar todos os usuários gerentes
            gerentes = Usuario.objects.filter(role=Usuario.Role.GERENTE)
            
            # Obter o content type do modelo de usuário personalizado
            usuario_content_type = ContentType.objects.get_for_model(Usuario)
            
            # Obter todas as permissões relacionadas a usuários e grupos
            user_perms = Permission.objects.filter(
                content_type=usuario_content_type
            ) | Permission.objects.filter(
                codename__in=['view_user', 'view_group']
            )
            
            # Para cada gerente, garantir que não tenha permissões de edição
            for gerente in gerentes:
                # Remover todas as permissões atuais
                gerente.user_permissions.clear()
                
                # Adicionar apenas as permissões de visualização
                view_user, created = Permission.objects.get_or_create(
                    codename='view_user',
                    defaults={
                        'name': 'Can view user',
                        'content_type': ContentType.objects.get_for_model(Usuario)
                    }
                )
                
                view_group, created = Permission.objects.get_or_create(
                    codename='view_group',
                    defaults={
                        'name': 'Can view group',
                        'content_type': ContentType.objects.get_for_model(Group)
                    }
                )
                
                gerente.user_permissions.add(view_user, view_group)
                
                # Garantir que o gerente não seja superusuário
                if gerente.is_superuser:
                    gerente.is_superuser = False
                
                # Garantir que o gerente não seja staff (a menos que seja necessário para o painel admin)
                gerente.is_staff = True
                
                gerente.save()
                
                self.stdout.write(self.style.SUCCESS(f'Permissões corrigidas para o gerente: {gerente.email}'))
            
            self.stdout.write(self.style.SUCCESS(f'Total de gerentes atualizados: {gerentes.count()}'))
