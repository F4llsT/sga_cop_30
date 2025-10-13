# apps/admin_personalizado/management/commands/send_custom_notifications.py
from django.core.management.base import BaseCommand
from apps.admin_personalizado.models import NotificacaoPersonalizada

class Command(BaseCommand):
    help = 'Envia notificações personalizadas pendentes'

    def handle(self, *args, **options):
        # Buscar notificações pendentes
        notificacoes = NotificacaoPersonalizada.objects.filter(status='pendente')
        
        if not notificacoes.exists():
            self.stdout.write(self.style.SUCCESS('Nenhuma notificação pendente para enviar.'))
            return
        
        self.stdout.write(f'Enviando {notificacoes.count()} notificação(ões) pendente(s)...')
        
        for notificacao in notificacoes:
            self.stdout.write(f'Enviando notificação: {notificacao.titulo}...')
            sucesso, mensagem = notificacao.enviar_notificacoes()
            
            if sucesso:
                self.stdout.write(self.style.SUCCESS(f'Sucesso: {mensagem}'))
            else:
                self.stdout.write(self.style.ERROR(f'Erro: {mensagem}'))
        
        self.stdout.write(self.style.SUCCESS('Processamento de notificações concluído.'))