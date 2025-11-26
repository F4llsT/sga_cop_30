import uuid
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from apps.passefacil.models import PasseFacil

User = get_user_model()

class Command(BaseCommand):
    help = 'Força a criação de Passe Fácil para todos os usuários que ainda não possuem'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirmar',
            action='store_true',
            help='Confirma a criação sem pedir confirmação'
        )
        parser.add_argument(
            '--usuarios-ativos',
            action='store_true',
            help='Cria apenas para usuários ativos (is_active=True)'
        )
        parser.add_argument(
            '--ignorar-staff',
            action='store_true',
            help='Ignora usuários staff (is_staff=True)'
        )

    def handle(self, *args, **options):
        confirmar = options['confirmar']
        usuarios_ativos = options['usuarios_ativos']
        ignorar_staff = options['ignorar_staff']
        
        # Query base de usuários
        usuarios_query = User.objects.all()
        
        # Aplicar filtros
        if usuarios_ativos:
            usuarios_query = usuarios_query.filter(is_active=True)
        
        if ignorar_staff:
            usuarios_query = usuarios_query.filter(is_staff=False)
        
        # Encontrar usuários que ainda não têm Passe Fácil
        usuarios_sem_passe = usuarios_query.exclude(
            passe_facil__isnull=False
        )
        
        total_usuarios = usuarios_query.count()
        usuarios_com_passe = total_usuarios - usuarios_sem_passe.count()
        usuarios_para_criar = usuarios_sem_passe.count()
        
        if usuarios_para_criar == 0:
            self.stdout.write(
                self.style.SUCCESS('✅ Todos os usuários já possuem Passe Fácil!')
            )
            self.stdout.write(f'   • Total de usuários: {total_usuarios}')
            self.stdout.write(f'   • Com Passe Fácil: {usuarios_com_passe}')
            return
        
        # Mostrar informações
        self.stdout.write(
            self.style.WARNING(f'📊 Análise de Passe Fácil:')
        )
        self.stdout.write(f'   • Total de usuários: {total_usuarios}')
        self.stdout.write(f'   • Já possuem Passe Fácil: {usuarios_com_passe}')
        self.stdout.write(f'   • Precisam criar Passe Fácil: {usuarios_para_criar}')
        
        # Mostrar alguns exemplos
        exemplos = usuarios_sem_passe[:5]
        if exemplos:
            self.stdout.write(f'\n📝 Exemplos de usuários que receberão Passe Fácil:')
            for usuario in exemplos:
                nome_completo = getattr(usuario, 'get_full_name', lambda: None)()
                nome = nome_completo or getattr(usuario, 'nome', None) or getattr(usuario, 'username', 'Usuário')
                status = "🟢 Ativo" if usuario.is_active else "🔴 Inativo"
                staff = "👨‍💼 Staff" if usuario.is_staff else "👤 Comum"
                self.stdout.write(f'   • {nome} ({status}, {staff})')
        
        if usuarios_para_criar > 5:
            self.stdout.write(f'   ... e mais {usuarios_para_criar - 5} usuários')
        
        if not confirmar:
            confirmacao = input(f'\n❓ Deseja criar Passe Fácil para {usuarios_para_criar} usuários? (SIM/NÃO): ')
            if confirmacao != 'SIM':
                self.stdout.write(self.style.ERROR('❌ Operação cancelada.'))
                return
        
        # Criar Passe Fácil para todos os usuários
        self.stdout.write(f'\n🔧 Criando Passe Fácil para {usuarios_para_criar} usuários...')
        
        criados = 0
        erros = 0
        
        with transaction.atomic():
            for usuario in usuarios_sem_passe:
                try:
                    # Verificar se não foi criado por outra transação
                    if not hasattr(usuario, 'passe_facil'):
                        passe = PasseFacil.objects.create(
                            user=usuario,
                            codigo=uuid.uuid4(),
                            ativo=True
                        )
                        criados += 1
                        
                        if criados % 10 == 0:
                            self.stdout.write(f'  ✅ {criados} passes criados...')
                    
                except Exception as e:
                    self.stderr.write(f'❌ Erro ao criar Passe Fácil para {usuario}: {str(e)}')
                    erros += 1
                    continue
        
        # Relatório final
        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 Operação concluída!')
        )
        self.stdout.write(f'   • Passes criados: {criados}')
        
        if erros > 0:
            self.stdout.write(
                self.style.WARNING(f'   • Erros: {erros}')
            )
        
        # Verificação final
        total_final = PasseFacil.objects.count()
        self.stdout.write(
            self.style.SUCCESS(f'\n📈 Estatísticas finais:')
        )
        self.stdout.write(f'   • Total de Passe Fácil no sistema: {total_final}')
        self.stdout.write(f'   • Usuários com Passe Fácil: {total_final}')
        self.stdout.write(f'   • Taxa de cobertura: {(total_final / total_usuarios * 100):.1f}%')
        
        # Mostrar alguns passes criados
        if criados > 0:
            passes_criados = PasseFacil.objects.select_related('user').order_by('-id')[:3]
            self.stdout.write(f'\n📋 Exemplos de passes criados:')
            for passe in passes_criados:
                nome = (getattr(passe.user, 'get_full_name', lambda: None)() or 
                       getattr(passe.user, 'nome', None) or 
                       getattr(passe.user, 'username', 'Usuário'))
                self.stdout.write(f'   • {nome}: {passe.codigo}')
        
        # Orientações
        self.stdout.write(
            self.style.SUCCESS(f'\n💡 Próximos passos:')
        )
        self.stdout.write(f'   • Usuários podem acessar: /passefacil/')
        self.stdout.write(f'   • Admin pode gerenciar: /meu-admin/passe-facil/')
        self.stdout.write(f'   • QR Codes válidos por 60 segundos')
        
        if criados == usuarios_para_criar:
            self.stdout.write(
                self.style.SUCCESS(f'\n🎯 SUCESSO: Todos os usuários agora possuem Passe Fácil!')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'\n⚠️  Alguns passes não puderam ser criados. Verifique os erros acima.')
            )
