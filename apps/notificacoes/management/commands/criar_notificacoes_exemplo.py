from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.notificacoes.models import Notificacao, NotificacaoUsuario

User = get_user_model()

class Command(BaseCommand):
    help = 'Cria notificações de exemplo para demonstração'

    def handle(self, *args, **options):
        # Busca todos os usuários ativos
        usuarios_ativos = User.objects.filter(is_active=True)
        
        if not usuarios_ativos.exists():
            # Se não houver usuários ativos, cria um admin padrão
            admin_user = User.objects.create_user(
                email='admin@cop30.com',
                nome='Administrador',
                password='admin123',
                is_staff=True,
                is_superuser=True
            )
            usuarios_ativos = [admin_user]
            self.stdout.write(
                self.style.SUCCESS(f'Usuário admin@cop30.com criado com sucesso!')
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

        total_notificacoes = 0
        total_usuarios = 0
        
        for usuario in usuarios_ativos:
            # Remove notificações existentes do usuário
            NotificacaoUsuario.objects.filter(usuario=usuario).delete()
            
            # Cria as novas notificações para cada usuário
            for notif_data in notificacoes_exemplo:
                # Cria a notificação
                notificacao = Notificacao.objects.create(
                    titulo=notif_data['titulo'],
                    mensagem=notif_data['mensagem'],
                    tipo=notif_data['tipo'],
                    criado_por=usuario
                )
                
                # Cria o relacionamento com o usuário
                NotificacaoUsuario.objects.create(
                    notificacao=notificacao,
                    usuario=usuario,
                    lida=notif_data['lida'],
                    lida_em=timezone.now() if notif_data['lida'] else None
                )
            
            total_usuarios += 1
            total_notificacoes += len(notificacoes_exemplo)
            
            self.stdout.write(
                self.style.SUCCESS(f'Criadas {len(notificacoes_exemplo)} notificações para {usuario.email}')
            )
        
        # Mostra estatísticas gerais
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('Resumo da operação:'))
        self.stdout.write(f'Total de usuários processados: {total_usuarios}')
        self.stdout.write(f'Total de notificações criadas: {total_notificacoes}')
        
        # Estatísticas gerais
        total_geral = Notificacao.objects.count()
        nao_lidas_geral = NotificacaoUsuario.objects.filter(lida=False).count()
        
        self.stdout.write(f'\nTotal geral de notificações no sistema: {total_geral}')
        self.stdout.write(f'Total de notificações não lidas: {nao_lidas_geral}')
