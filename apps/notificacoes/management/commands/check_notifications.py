from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.notificacoes.models import Notificacao

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
            notificacoes = Notificacao.objects.filter(usuario=user)
            
            if apenas_nao_lidas:
                notificacoes = notificacoes.filter(lida=False)
                
            total = notificacoes.count()
            nao_lidas = notificacoes.filter(lida=False).count()
            
            self.stdout.write(f"\nUsuário: {user.email}")
            self.stdout.write(f"- Total de notificações: {total}")
            self.stdout.write(f"- Não lidas: {nao_lidas}")
            
            # Mostrar detalhes das notificações recentes (últimas 5)
            if total > 0:
                self.stdout.write("\n  Últimas notificações:")
                for notif in notificacoes.order_by('-criada_em')[:5]:
                    status = "[LIDA]" if notif.lida else "[NÃO LIDA]"
                    self.stdout.write(f"  - {notif.titulo} {status} ({notif.criada_em.strftime('%d/%m/%Y %H:%M')})")
        
        self.stdout.write(self.style.SUCCESS('\nVerificação de notificações concluída!'))
