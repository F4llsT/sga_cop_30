from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from apps.passefacil.models import ValidacaoQRCode

class Command(BaseCommand):
    help = 'Apaga todas as validações de Passe Fácil'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirmar',
            action='store_true',
            help='Executa sem pedir confirmação'
        )
        parser.add_argument(
            '--dias-recentes',
            type=int,
            help='Apaga apenas validacões dos últimos X dias'
        )

    def handle(self, *args, **options):
        confirmar = options['confirmar']
        dias_recentes = options['dias_recentes']
        
        self.stdout.write('🗑️  Comando de limpeza de validações Passe Fácil')
        
        # Contar validações existentes
        queryset = ValidacaoQRCode.objects.all()
        
        if dias_recentes:
            corte = timezone.now() - timezone.timedelta(days=dias_recentes)
            queryset = queryset.filter(data_validacao__gte=corte)
            self.stdout.write(f'📅 Período: Últimos {dias_recentes} dias')
        else:
            self.stdout.write(f'📅 Período: Todas as validações')
        
        total_apagar = queryset.count()
        
        if total_apagar == 0:
            self.stdout.write(
                self.style.SUCCESS('✅ Nenhuma validação encontrada para apagar!')
            )
            return
        
        # Mostrar estatísticas antes de apagar
        self.stdout.write(f'📊 Validacões encontradas: {total_apagar}')
        
        # Mostrar algumas validações mais recentes
        validacoes_recentes = queryset.order_by('-data_validacao')[:5]
        if validacoes_recentes:
            self.stdout.write('\n📋 Validacões mais recentes:')
            for i, validacao in enumerate(validacoes_recentes, 1):
                usuario = validacao.passe_facil.user.get_full_name() or validacao.passe_facil.user.username
                data = validacao.data_validacao.strftime('%d/%m/%Y %H:%M')
                status = '✅' if validacao.valido else '❌'
                self.stdout.write(f'   {i}. {usuario} - {data} - {status}')
        
        # Confirmar operação
        if not confirmar:
            self.stdout.write(f'\n⚠️  ATENÇÃO: Isso apagará {total_apagar} validacões permanentemente!')
            confirmacao = input('❓ Tem certeza que deseja continuar? (APAGAR TUDO/NÃO): ')
            if confirmacao != 'APAGAR TUDO':
                self.stdout.write(self.style.ERROR('❌ Operação cancelada.'))
                return
        
        # Apagar validações
        self.stdout.write('\n🔄 Apagando validações...')
        
        try:
            with transaction.atomic():
                # Estatísticas antes de apagar
                validacoes_sucesso = queryset.filter(valido=True).count()
                validacoes_falha = queryset.filter(valido=False).count()
                
                # Apagar
                apagadas, _ = queryset.delete()
                
                self.stdout.write(
                    self.style.SUCCESS(f'✅ {apagadas} validações apagadas com sucesso!')
                )
                
                # Estatísticas da operação
                self.stdout.write('\n📈 Resumo da operação:')
                self.stdout.write(f'   • Total apagado: {apagadas}')
                self.stdout.write(f'   • Válidas: {validacoes_sucesso}')
                self.stdout.write(f'   • Inválidas: {validacoes_falha}')
                
                # Verificar total restante
                total_restante = ValidacaoQRCode.objects.count()
                if total_restante > 0:
                    self.stdout.write(f'   • Restantes: {total_restante}')
                    
                    if dias_recentes:
                        self.stdout.write(f'\n💡 Para apagar tudo, use sem --dias-recentes')
                else:
                    self.stdout.write(f'   • Restantes: 0')
                    self.stdout.write(
                        self.style.SUCCESS('\n🎯 BANCO LIMPO: Todas as validações foram removidas!')
                    )
                
                # Orientações
                self.stdout.write(
                    self.style.SUCCESS(f'\n💡 Próximos passos:')
                )
                self.stdout.write(f'   • Gerar novos dados: python manage.py gerar_validacoes_teste')
                self.stdout.write(f'   • Ver dashboard: /meu-admin/passe-facil/')
                
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f'❌ Erro ao apagar validações: {str(e)}')
            )
            return
