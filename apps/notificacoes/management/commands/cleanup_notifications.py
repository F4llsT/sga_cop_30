# apps/notificacoes/management/commands/cleanup_notifications.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q
from apps.notificacoes.models import Notificacao

class Command(BaseCommand):
    help = 'Remove notificações expiradas ou antigas do banco de dados'

    def handle(self, *args, **options):
        agora = timezone.now()
        
        # Notificações lidas que expiraram (1 hora após leitura)
        read_expired = Notificacao.objects.filter(
            lida=True,
            lida_em__lt=agora - timezone.timedelta(hours=1)
        )
        
        # Notificações não lidas que expiraram (10 dias após criação)
        unread_expired = Notificacao.objects.filter(
            lida=False,
            criada_em__lt=agora - timezone.timedelta(days=10)
        )
        
        # Notificações com data de expiração manual
        manually_expired = Notificacao.objects.filter(
            data_expiracao__isnull=False,
            data_expiracao__lt=agora
        )
        
        # Combina todos os querysets
        to_delete = (read_expired | unread_expired | manually_expired).distinct()
        
        total = to_delete.count()
        
        if options.get('dry_run', False):
            self.stdout.write(self.style.WARNING('Modo de teste - Nenhuma notificação será removida'))
            self.stdout.write(f'Notificações lidas expiradas: {read_expired.count()}')
            self.stdout.write(f'Notificações não lidas antigas: {unread_expired.count()}')
            self.stdout.write(f'Notificações com expiração manual: {manually_expired.count()}')
            self.stdout.write(f'Total de notificações que seriam removidas: {total}')
            return
        
        # Remove as notificações
        deleted_count, _ = to_delete.delete()
        
        self.stdout.write(self.style.SUCCESS(
            f'Notificações removidas com sucesso: {deleted_count}'
        ))

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Executa em modo de teste sem deletar nada'
        )