from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.notificacoes.models import Aviso
from faker import Faker
import random
from datetime import timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Cria avisos de exemplo relacionados à COOP 30'

    def add_arguments(self, parser):
        parser.add_argument(
            'quantidade',
            type=int,
            nargs='?',
            default=5,
            help='Número de avisos a serem criados (padrão: 5)'
        )

    def handle(self, *args, **options):
        quantidade = options['quantidade']
        fake = Faker('pt_BR')
        
        # Verifica se existe um superusuário para ser o criador
        try:
            admin = User.objects.filter(is_superuser=True).first()
            if not admin:
                admin = User.objects.first()
                if not admin:
                    self.stdout.write(
                        self.style.ERROR('Nenhum usuário encontrado. Crie um usuário primeiro.')
                    )
                    return
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro ao buscar usuário: {str(e)}')
            )
            return

        # Lista de títulos relacionados à COOP 30
        titulos = [
            "Atualização do Regimento da COOP 30",
            "Reunião de Assembléia Geral - COOP 30",
            "Novos Benefícios para Cooperados",
            "Mudanças na Diretoria da COOP 30",
            "Resultados Financeiros do Último Trimestre",
            "Campanha de Adesão de Novos Cooperados",
            "Workshop de Educação Financeira",
            "Sorteio de Prêmios para Cooperados",
            "Reforma do Estatuto Social",
            "Programa de Desenvolvimento de Lideranças"
        ]

        # Lista de níveis de importância
        niveis = ['info', 'alerta', 'critico']
        
        # Lista de mensagens relacionadas à COOP 30
        mensagens = [
            "A COOP 30 está promovendo uma série de melhorias para nossos cooperados. Fique atento às novidades!",
            "Participe da nossa próxima assembleia geral e contribua com as decisões da nossa cooperativa.",
            "Novos benefícios disponíveis para todos os cooperados ativos. Confira no site ou na sede.",
            "A diretoria da COOP 30 tem o prazer de anunciar as novas lideranças que assumirão em breve.",
            "Nossos resultados financeiros mostram crescimento e estabilidade. Confira o relatório completo.",
            "Indique um amigo para ser cooperado e ganhe benefícios exclusivos na COOP 30.",
            "Participe do nosso workshop de educação financeira e aprenda a gerenciar melhor seus recursos.",
            "Sorteio exclusivo para cooperados ativos. Confira o regulamento e participe!",
            "Estamos atualizando nosso estatuto social. Sua opinião é importante para nós.",
            "Inscrições abertas para o programa de desenvolvimento de lideranças da COOP 30."
        ]

        avisos_criados = 0
        
        for i in range(quantidade):
            try:
                # Seleciona um título e uma mensagem aleatória
                titulo = random.choice(titulos)
                mensagem = random.choice(mensagens)
                
                # Garante que título e mensagem sejam diferentes
                while titulo.lower() in mensagem.lower() or len(mensagem) < 30:
                    mensagem = random.choice(mensagens)
                
                # Cria o aviso
                aviso = Aviso.objects.create(
                    titulo=titulo,
                    mensagem=mensagem,
                    nivel=random.choice(niveis),
                    criado_por=admin,
                    data_expiracao=timezone.now() + timedelta(days=random.randint(1, 90)),
                    fixo_no_topo=random.choice([True, False]),
                    ativo=random.choice([True, True, True, False])  # 75% de chance de estar ativo
                )
                
                avisos_criados += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Aviso criado: {aviso.titulo}')
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Erro ao criar aviso: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n{avisos_criados} avisos criados com sucesso!')
        )
