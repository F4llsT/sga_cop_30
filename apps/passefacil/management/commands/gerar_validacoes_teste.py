import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction, models
from django.utils import timezone
from apps.passefacil.models import PasseFacil, ValidacaoQRCode

User = get_user_model()

class Command(BaseCommand):
    help = 'Cria validações de Passe Fácil com usuários e datas aleatórias'

    def add_arguments(self, parser):
        parser.add_argument(
            '--quantidade',
            type=int,
            default=100,
            help='Número de validações a criar (padrão: 100)'
        )
        parser.add_argument(
            '--dias-atras',
            type=int,
            default=120,
            help='Número máximo de dias para trás (padrão: 120)'
        )
        parser.add_argument(
            '--usuarios-ativos',
            action='store_true',
            help='Usa apenas usuários com Passe Fácil ativo'
        )
        parser.add_argument(
            '--confirmar',
            action='store_true',
            help='Executa sem pedir confirmação'
        )
        parser.add_argument(
            '--taxa-sucesso',
            type=float,
            default=0.85,
            help='Taxa de sucesso das validações (0.0-1.0, padrão: 0.85)'
        )

    def handle(self, *args, **options):
        quantidade = options['quantidade']
        dias_atras = options['dias_atras']
        usuarios_ativos = options['usuarios_ativos']
        confirmar = options['confirmar']
        taxa_sucesso = options['taxa_sucesso']
        
        self.stdout.write(f'🔧 Gerando {quantidade} validações de Passe Fácil...')
        self.stdout.write(f'📅 Período: Últimos {dias_atras} dias')
        self.stdout.write(f'✅ Taxa de sucesso: {taxa_sucesso*100:.1f}%')
        
        # Buscar usuários com Passe Fácil
        usuarios_com_passe = User.objects.filter(passe_facil__isnull=False)
        
        if usuarios_ativos:
            usuarios_com_passe = usuarios_com_passe.filter(passe_facil__ativo=True)
        
        total_usuarios = usuarios_com_passe.count()
        
        if total_usuarios == 0:
            self.stdout.write(
                self.style.ERROR('❌ Nenhum usuário com Passe Fácil encontrado!')
            )
            self.stdout.write('   • Crie passes primeiro: python manage.py criar_passe_facil_todos')
            return
        
        self.stdout.write(f'👥 Usuários disponíveis: {total_usuarios}')
        
        # Verificar validações existentes
        validacoes_existentes = ValidacaoQRCode.objects.count()
        self.stdout.write(f'📊 Validacões existentes: {validacoes_existentes}')
        
        if not confirmar:
            confirmacao = input(f'\n❓ Deseja criar {quantidade} validações aleatórias? (SIM/NÃO): ')
            if confirmacao != 'SIM':
                self.stdout.write(self.style.ERROR('❌ Operação cancelada.'))
                return
        
        # Lista de IPs fictícios para variedade
        ips_ficticios = [
            '192.168.1.10', '192.168.1.20', '192.168.1.30', '192.168.1.40',
            '192.168.1.50', '192.168.1.60', '192.168.1.70', '192.168.1.80',
            '10.0.0.15', '10.0.0.25', '10.0.0.35', '10.0.0.45',
            '172.16.0.5', '172.16.0.15', '172.16.0.25', '172.16.0.35'
        ]
        
        # Criar validações
        criadas = 0
        erros = 0
        
        with transaction.atomic():
            for i in range(quantidade):
                try:
                    # Selecionar usuário aleatório
                    usuario = random.choice(usuarios_com_passe)
                    passe_facil = usuario.passe_facil
                    
                    # Gerar data aleatória (entre hoje e dias_atras para trás)
                    dias_aleatorios = random.randint(0, dias_atras)
                    horas_aleatorias = random.randint(0, 23)
                    minutos_aleatorios = random.randint(0, 59)
                    
                    # Gerar data no passado usando timedelta corretamente
                    agora = timezone.now()
                    data_validacao = agora - timedelta(
                        days=dias_aleatorios,
                        hours=horas_aleatorias,
                        minutes=minutos_aleatorios
                    )
                    
                    # Debug: mostrar algumas datas geradas
                    if i < 3:
                        self.stdout.write(f'  📅 Debug {i+1}: {dias_aleatorios} dias atrás -> {data_validacao.strftime("%d/%m/%Y %H:%M")}')
                    
                    # Gerar código (pode ser o UUID do passe ou um código aleatório)
                    sucesso = random.random() < taxa_sucesso
                    
                    if sucesso:
                        codigo_validado = str(passe_facil.codigo)
                    else:
                        # Código inválido aleatório
                        codigo_validado = f"{random.randint(100000, 999999)}-{random.randint(10, 99)}"
                    
                    # Selecionar IP aleatório
                    ip_address = random.choice(ips_ficticios)
                    
                    # Criar validação
                    validacao = ValidacaoQRCode.objects.create(
                        passe_facil=passe_facil,
                        codigo=codigo_validado,
                        data_validacao=data_validacao,
                        valido=sucesso,
                        ip_address=ip_address
                    )
                    
                    criadas += 1
                    
                    if criadas % 20 == 0:
                        self.stdout.write(f'  ✅ {criadas} validações criadas...')
                
                except Exception as e:
                    self.stderr.write(f'❌ Erro ao criar validação {i+1}: {str(e)}')
                    erros += 1
                    continue
        
        # Relatório final
        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 Operação concluída!')
        )
        self.stdout.write(f'   • Validacões criadas: {criadas}')
        
        if erros > 0:
            self.stdout.write(
                self.style.WARNING(f'   • Erros: {erros}')
            )
        
        # Estatísticas
        total_final = ValidacaoQRCode.objects.count()
        validacoes_sucesso = ValidacaoQRCode.objects.filter(valido=True).count()
        validacoes_falha = total_final - validacoes_sucesso
        
        self.stdout.write(
            self.style.SUCCESS(f'\n📈 Estatísticas finais:')
        )
        self.stdout.write(f'   • Total de validacões: {total_final}')
        self.stdout.write(f'   • Sucesso: {validacoes_sucesso} ({(validacoes_sucesso/total_final*100):.1f}%)')
        self.stdout.write(f'   • Falha: {validacoes_falha} ({(validacoes_falha/total_final*100):.1f}%)')
        
        # Top usuários
        top_usuarios = (
            ValidacaoQRCode.objects
            .values('passe_facil__user__nome')
            .annotate(total=models.Count('id'))
            .order_by('-total')[:5]
        )
        
        if top_usuarios:
            self.stdout.write(f'\n🏆 Top 5 usuários mais validados:')
            for i, item in enumerate(top_usuarios, 1):
                nome = item['passe_facil__user__nome'] or 'Usuário'
                self.stdout.write(f'   {i}. {nome}: {item["total"]} validações')
        
        # Distribuição por período
        hoje = timezone.now().date()
        validacoes_7dias = ValidacaoQRCode.objects.filter(
            data_validacao__gte=hoje - timedelta(days=7)
        ).count()
        validacoes_30dias = ValidacaoQRCode.objects.filter(
            data_validacao__gte=hoje - timedelta(days=30)
        ).count()
        
        self.stdout.write(f'\n📊 Validacões por período:')
        self.stdout.write(f'   • Últimos 7 dias: {validacoes_7dias}')
        self.stdout.write(f'   • Últimos 30 dias: {validacoes_30dias}')
        
        # IPs mais utilizados
        ips = (
            ValidacaoQRCode.objects
            .values('ip_address')
            .annotate(total=models.Count('id'))
            .order_by('-total')[:3]
        )
        
        if ips:
            self.stdout.write(f'\n🌐 IPs mais utilizados:')
            for item in ips:
                self.stdout.write(f'   • {item["ip_address"]}: {item["total"]} validações')
        
        # Orientações
        self.stdout.write(
            self.style.SUCCESS(f'\n💡 Próximos passos:')
        )
        self.stdout.write(f'   • Ver dashboard: /meu-admin/passe-facil/')
        self.stdout.write(f'   • Analisar relatórios e estatísticas')
        self.stdout.write(f'   • Usar dados para testes de performance')
        
        if criadas == quantidade:
            self.stdout.write(
                self.style.SUCCESS(f'\n🎯 SUCESSO: {quantidade} validações criadas com sucesso!')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'\n⚠️  Algumas validações não puderam ser criadas. Verifique os erros acima.')
            )
