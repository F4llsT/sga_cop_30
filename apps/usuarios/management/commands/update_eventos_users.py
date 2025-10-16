from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from apps.agenda.models import Event

User = get_user_model()

class Command(BaseCommand):
    help = 'Atualiza os usuários de eventos para terem is_staff=True e as permissões necessárias'

    def handle(self, *args, **options):
        # Atualiza todos os usuários de eventos para terem is_staff=True
        updated = User.objects.filter(role='EVENTOS', is_staff=False).update(is_staff=True)
        
        # Obtém todos os usuários de eventos
        usuarios_eventos = User.objects.filter(role='EVENTOS')
        
        # Obtém as permissões de evento
        content_type = ContentType.objects.get_for_model(Event)
        permissoes = content_type.permission_set.all()
        
        # Adiciona as permissões a cada usuário de eventos
        for usuario in usuarios_eventos:
            usuario.user_permissions.set(permissoes)
            self.stdout.write(self.style.SUCCESS(f'Atualizado usuário: {usuario.email}'))
        
        self.stdout.write(
            self.style.SUCCESS(f'Concluído! {updated} usuários de eventos foram atualizados.')
        )
