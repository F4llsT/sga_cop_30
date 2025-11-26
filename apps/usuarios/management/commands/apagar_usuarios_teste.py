from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

class Command(BaseCommand):
    help = 'Apaga usuários de teste criados pelo comando criar_usuarios_teste'

    def add_arguments(self, parser):
        parser.add_argument(
            '--prefixo',
            type=str,
            default='teste',
            help='Prefixo dos usuários a apagar (padrão: teste)'
        )
        parser.add_argument(
            '--confirmar',
            action='store_true',
            help='Confirma a exclusão sem pedir confirmação'
        )

    def handle(self, *args, **options):
        prefixo = options['prefixo']
        confirmar = options['confirmar']
        
        # Conta quantos usuários serão afetados (usando campo 'nome')
        usuarios_para_apagar = User.objects.filter(nome__startswith=prefixo)
        total_usuarios = usuarios_para_apagar.count()
        
        if total_usuarios == 0:
            self.stdout.write(
                self.style.WARNING(f'⚠️  Nenhum usuário encontrado com prefixo "{prefixo}"')
            )
            return
        
        self.stdout.write(
            self.style.WARNING(f'⚠️  Você está prestes a apagar {total_usuarios} usuários com prefixo "{prefixo}"')
        )
        
        # Mostra alguns exemplos
        exemplos = usuarios_para_apagar[:5]
        if exemplos:
            self.stdout.write(f'\n📝 Exemplos de usuários que serão apagados:')
            for usuario in exemplos:
                self.stdout.write(f'   • {usuario.nome} ({usuario.email})')
            if total_usuarios > 5:
                self.stdout.write(f'   ... e mais {total_usuarios - 5} usuários')
        
        if not confirmar:
            confirmacao = input('\nDigite "SIM" para confirmar a exclusão: ')
            if confirmacao != 'SIM':
                self.stdout.write(self.style.ERROR('❌ Operação cancelada.'))
                return
        
        try:
            with transaction.atomic():
                nomes_apagados = list(usuarios_para_apagar.values_list('nome', flat=True))
                usuarios_apagados, _ = usuarios_para_apagar.delete()
                
                self.stdout.write(
                    self.style.SUCCESS(f'\n✅ {usuarios_apagados} usuários apagados com sucesso!')
                )
                
                # Mostra os nomes apagados
                if len(nomes_apagados) <= 10:
                    self.stdout.write(f'\n📋 Usuários removidos:')
                    for nome in nomes_apagados:
                        self.stdout.write(f'   • {nome}')
                else:
                    self.stdout.write(f'\n📋 Primeiros 10 usuários removidos:')
                    for nome in nomes_apagados[:10]:
                        self.stdout.write(f'   • {nome}')
                    self.stdout.write(f'   ... e mais {len(nomes_apagados) - 10} usuários')
                
                # Verificação final
                restantes = User.objects.filter(nome__startswith=prefixo).count()
                if restantes == 0:
                    self.stdout.write(
                        self.style.SUCCESS(f'\n🎉 Todos os usuários com prefixo "{prefixo}" foram removidos!')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  Ainda restam {restantes} usuários com prefixo "{prefixo}"')
                    )
                        
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro ao apagar usuários: {str(e)}')
            )
            return
