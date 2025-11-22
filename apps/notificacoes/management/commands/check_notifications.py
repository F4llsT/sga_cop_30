from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.notificacoes.models import Notificacao, NotificacaoUsuario

User = get_user_model()

class Command(BaseCommand):
    help = 'Verifica as notificações dos usuários e exibe estatísticas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Filtrar por email do usuário',
        )
        parser.add_argument(
            '--nao-lidas',
            action='store_true',
            help='Mostrar apenas notificações não lidas',
        )

    def handle(self, *args, **options):
        users = User.objects.all()
        email = options.get('email')
        apenas_nao_lidas = options.get('nao_lidas')
        
        if email:
            users = users.filter(email__icontains=email)
            
        total_usuarios = users.count()
        self.stdout.write(self.style.SUCCESS(f'Total de usuários: {total_usuarios}'))
        
        if total_usuarios == 0:
            self.stdout.write(self.style.WARNING('Nenhum usuário encontrado com os critérios fornecidos.'))
            return
            
        for user in users:
            # Obtém as notificações do usuário através do modelo NotificacaoUsuario
            notificacoes_usuario = NotificacaoUsuario.objects.filter(usuario=user)
            
            if apenas_nao_lidas:
                notificacoes_usuario = notificacoes_usuario.filter(lida=False)
                
            total = notificacoes_usuario.count()
            nao_lidas = notificacoes_usuario.filter(lida=False).count()
            
            self.stdout.write(f"\nUsuário: {user.email}")
            self.stdout.write(f"- Total de notificações: {total}")
            self.stdout.write(f"- Não lidas: {nao_lidas}")
            
            # Mostrar detalhes das notificações recentes (últimas 5)
            if total > 0:
                self.stdout.write("\n  Últimas notificações:")
                for rel_usuario in notificacoes_usuario.select_related('notificacao').order_by('-notificacao__criada_em')[:5]:
                    notif = rel_usuario.notificacao
                    status = 'NÃO LIDA' if not rel_usuario.lida else 'LIDA'
                    self.stdout.write(f"  - {notif.titulo} ({status}) - {notif.criada_em.strftime('%d/%m/%Y %H:%M')}")
                    if rel_usuario.lida and rel_usuario.lida_em:
                        self.stdout.write(f"    Lida em: {rel_usuario.lida_em.strftime('%d/%m/%Y %H:%M')}")

        self.stdout.write(self.style.SUCCESS('\nVerificação de notificações concluída!'))
