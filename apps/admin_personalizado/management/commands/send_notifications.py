from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.notificacoes.models import Notificacao, NotificacaoUsuario

class Command(BaseCommand):
    help = 'Envia notificações pendentes para os usuários'

    def handle(self, *args, **options):
        # Obtém todas as notificações não lidas através do modelo NotificacaoUsuario
        notificacoes_usuarios = NotificacaoUsuario.objects.filter(
            lida=False
        ).select_related('notificacao', 'usuario').order_by('notificacao__criada_em')
        
        if not notificacoes_usuarios.exists():
            self.stdout.write(self.style.SUCCESS('Nenhuma notificação não lida encontrada.'))
            return
        
        self.stdout.write(f'Encontradas {notificacoes_usuarios.count()} notificações não lidas')
        
        for notificacao_usuario in notificacoes_usuarios:
            notificacao = notificacao_usuario.notificacao
            usuario = notificacao_usuario.usuario
            
            self.stdout.write(f'Processando notificação: {notificacao.titulo} para {usuario.get_full_name() or usuario.email}')
            
            try:
                # Aqui você pode adicionar lógica para enviar notificações por e-mail, push, etc.
                # Por exemplo:
                # enviar_email_notificacao(notificacao, usuario)
                
                # Marcar como lida após o envio (opcional)
                # notificacao.marcar_como_lida(usuario)
                
                self.stdout.write(
                    self.style.SUCCESS(f'Notificação "{notificacao.titulo}" processada para {usuario.get_full_name() or usuario.email}')
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Erro ao processar notificação {notificacao.id}: {str(e)}')
                )