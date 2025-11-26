import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

class Command(BaseCommand):
    help = 'Cria usuários aleatórios para testes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--quantidade',
            type=int,
            default=10,
            help='Número de usuários a criar (padrão: 10)'
        )
        parser.add_argument(
            '--prefixo',
            type=str,
            default='teste',
            help='Prefixo para os nomes de usuário (padrão: teste)'
        )

    def handle(self, *args, **options):
        quantidade = options['quantidade']
        prefixo = options['prefixo']
        
        self.stdout.write(f'🔧 Criando {quantidade} usuários de teste com prefixo "{prefixo}"...')
        
        # Listas para geração de dados aleatórios
        dominios = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'teste.com']
        
        usuarios_criados = 0
        erros = 0
        
        with transaction.atomic():
            for i in range(quantidade):
                try:
                    # Gera número único para evitar duplicatas
                    numero_unico = random.randint(1000, 9999)
                    nome = f'{prefixo}{numero_unico}'
                    email = f'{nome}@{random.choice(dominios)}'
                    
                    # Verifica se já existe (usando o campo 'nome')
                    if User.objects.filter(nome=nome).exists():
                        erros += 1
                        continue
                    
                    # Cria o usuário sem first_name e last_name
                    usuario = User.objects.create_user(
                        nome=nome,  # Usa o campo 'nome' em vez de 'username'
                        email=email,
                        password='senha123',  # Senha padrão para todos
                        is_active=True,
                        is_staff=False,  # Não é staff por padrão
                        is_superuser=False
                    )
                    
                    usuarios_criados += 1
                    
                    if usuarios_criados % 5 == 0:
                        self.stdout.write(f'  ✅ {usuarios_criados} usuários criados...')
                        
                except Exception as e:
                    self.stderr.write(f'❌ Erro ao criar usuário {i+1}: {str(e)}')
                    erros += 1
                    continue
        
        # Relatório final
        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 Usuários criados com sucesso!')
        )
        self.stdout.write(f'   • Usuários criados: {usuarios_criados}')
        
        if erros > 0:
            self.stdout.write(
                self.style.WARNING(f'   • Erros/duplicatas: {erros}')
            )
        
        # Mostra alguns exemplos
        if usuarios_criados > 0:
            exemplos = User.objects.filter(nome__startswith=prefixo)[:3]
            self.stdout.write(f'\n📝 Exemplos de usuários criados:')
            for usuario in exemplos:
                self.stdout.write(f'   • Nome: {usuario.nome} | Email: {usuario.email} | Senha: senha123')
        
        self.stdout.write(
            self.style.SUCCESS(f'\n🔑 Todos os usuários foram criados com a senha padrão: "senha123"')
        )
        self.stdout.write(
            self.style.SUCCESS(f'🔍 Para apagar esses usuários, use: python manage.py apagar_usuarios_teste --prefixo {prefixo}')
        )
