from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.notificacoes.models import Notificacao

User = get_user_model()

class Command(BaseCommand):
    help = 'Cria notificações de exemplo para demonstração'

    def handle(self, *args, **options):
        # Busca o primeiro usuário ou cria um se não existir
        user, created = User.objects.get_or_create(
            email='admin@cop30.com',
            defaults={
                'nome': 'Administrador',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created:
            user.set_password('admin123')
            user.save()
            self.stdout.write(
                self.style.SUCCESS(f'Usuário {user.email} criado com sucesso!')
            )

        # Cria notificações de exemplo
        notificacoes_exemplo = [
            {
                'titulo': 'Bem-vindo ao COP30!',
                'mensagem': 'Sua conta foi criada com sucesso. Explore todas as funcionalidades disponíveis.',
                'tipo': 'info',
                'lida': False
            },
            {
                'titulo': 'Evento confirmado',
                'mensagem': 'Sua participação no evento "Sustentabilidade e Meio Ambiente" foi confirmada para amanhã às 14h.',
                'tipo': 'success',
                'lida': False
            },
            {
                'titulo': 'Lembrete importante',
                'mensagem': 'Não esqueça de trazer seu documento de identidade e comprovante de vacinação.',
                'tipo': 'warning',
                'lida': True
            },
            {
                'titulo': 'Atualização do sistema',
                'mensagem': 'O sistema passou por uma atualização. Algumas funcionalidades podem ter mudado.',
                'tipo': 'info',
                'lida': False
            },
            {
                'titulo': 'Alerta de segurança',
                'mensagem': 'Mantenha seus dados pessoais seguros. Não compartilhe suas credenciais de acesso.',
                'tipo': 'error',
                'lida': False
            }
        ]

        # Remove notificações existentes do usuário
        Notificacao.objects.filter(usuario=user).delete()

        # Cria as novas notificações
        for notif_data in notificacoes_exemplo:
            Notificacao.objects.create(
                usuario=user,
                **notif_data
            )

        self.stdout.write(
            self.style.SUCCESS(f'Criadas {len(notificacoes_exemplo)} notificações de exemplo para {user.email}')
        )
        
        # Mostra estatísticas
        total = Notificacao.objects.filter(usuario=user).count()
        nao_lidas = Notificacao.objects.filter(usuario=user, lida=False).count()
        
        self.stdout.write(f'Total de notificações: {total}')
        self.stdout.write(f'Notificações não lidas: {nao_lidas}')
