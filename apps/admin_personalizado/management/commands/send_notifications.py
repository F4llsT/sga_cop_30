from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.admin_personalizado.models import NotificacaoPersonalizada

class Command(BaseCommand):
    help = 'Envia notificações pendentes para os usuários'

    def handle(self, *args, **options):
        # Get pending notifications
        notificacoes_pendentes = NotificacaoPersonalizada.objects.filter(
            status='pendente'
        ).order_by('data_criacao')
        
        if not notificacoes_pendentes.exists():
            self.stdout.write(self.style.SUCCESS('Nenhuma notificação pendente para enviar.'))
            return
        
        self.stdout.write(f'Encontrando notificações pendentes: {notificacoes_pendentes.count()}')
        
        for notificacao in notificacoes_pendentes:
            self.stdout.write(f'Enviando notificação: {notificacao.titulo}')
            sucesso, mensagem = notificacao.enviar_notificacoes()
            
            if sucesso:
                self.stdout.write(
                    self.style.SUCCESS(f'Sucesso: {mensagem}')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'Erro: {mensagem}')
                )