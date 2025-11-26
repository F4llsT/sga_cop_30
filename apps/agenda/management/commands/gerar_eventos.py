import os
import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import models
from apps.agenda.models import Event

# Dados de exemplo para geração de eventos
titulos = [
    "COP30: Rumo à Neutralidade de Carbono",
    "Diálogos sobre a Amazônia na COP30",
    "Tecnologias para o Desmatamento Zero",
    "Financiamento Climático na Prática",
    "Comunidades Tradicionais e Mudanças Climáticas",
    "Energias Renováveis na Amazônia",
    "Adaptação às Mudanças Climáticas no Norte do Brasil",
    "Biodiversidade e Economia Verde",
    "Justiça Climática e Direitos Humanos",
    "Soluções Baseadas na Natureza"
]

descricoes = [
    "Discussões sobre as estratégias para alcançar a neutralidade de carbono até 2050, tema central da COP30.",
    "Painel com lideranças indígenas e especialistas sobre o papel da Amazônia no equilíbrio climático global.",
    "Apresentação de inovações tecnológicas para monitoramento e combate ao desmatamento na região amazônica.",
    "Workshop sobre mecanismos de financiamento para projetos de mitigação e adaptação às mudanças climáticas.",
    "Roda de conversa com representantes de comunidades tradicionais sobre impactos e soluções climáticas.",
    "Debate sobre o potencial das energias renováveis na região amazônica e seus desafios.",
    "Estratégias de adaptação para os impactos das mudanças climáticas na região Norte do Brasil.",
    "Como conciliar conservação da biodiversidade com desenvolvimento econômico sustentável.",
    "Discussão sobre os aspectos de justiça climática e a proteção dos direitos humanos em um mundo em mudança.",
    "Apresentação de casos de sucesso de soluções baseadas na natureza para desafios climáticos."
]

locais = [
    "Auditório Principal",
    "Sala de Workshop 1",
    "Área de Exposições",
    "Sala de Reuniões 3",
    "Auditório Verde",
    "Espaço de Eventos Sustentáveis",
    "Sala de Palestras 2",
    "Área de Convivência",
    "Sala de Treinamento",
    "Auditório Central"
]

palestrantes = [
    "Dr. João Silva",
    "Profa. Maria Oliveira",
    "Eng. Carlos Santos",
    "Dra. Ana Pereira",
    "Dr. Marcos Costa",
    "Profa. Juliana Almeida",
    "Eng. Ricardo Nunes",
    "Dra. Patrícia Lima",
    "Dr. Fernando Rocha",
    "Profa. Camila Martins"
]

tags = [
    'sustentabilidade', 'meio ambiente', 'reciclagem', 'energia renovável',
    'agricultura urbana', 'consumo consciente', 'mudanças climáticas',
    'construção sustentável', 'empreendedorismo', 'tecnologia verde'
]

class Command(BaseCommand):
    help = 'Gera eventos de teste para o sistema de agenda'

    def add_arguments(self, parser):
        parser.add_argument(
            'quantidade',
            type=int,
            nargs='?',
            default=10,
            help='Número de eventos a serem criados (padrão: 10)'
        )

    def gerar_coordenadas(self):
        # Gera coordenadas aleatórias próximas a Belém do Pará
        # Latitude: -1.4558 ± 0.1, Longitude: -48.4902 ± 0.1
        latitude = round(-1.4558 + random.uniform(-0.1, 0.1), 6)
        longitude = round(-48.4902 + random.uniform(-0.1, 0.1), 6)
        return latitude, longitude

    def criar_eventos_teste(self, quantidade=10):
        """
        Cria um número especificado de eventos de teste.
        
        Args:
            quantidade (int): Número de eventos a serem criados
        """
        # Obtém o primeiro usuário disponível (ou cria um se não existir)
        User = get_user_model()
        try:
            usuario = User.objects.first()
            if not usuario:
                usuario = User.objects.create_user(
                    username='admin',
                    email='admin@example.com',
                    password='admin123',
                    is_staff=True,
                    is_superuser=True
                )
                self.stdout.write(self.style.SUCCESS('Usuário admin criado com sucesso!'))
        except Exception as e:
            self.stderr.write(f"Erro ao obter/criar usuário: {e}")
            return

        # Gera eventos de teste
        eventos_criados = 0
        hoje = datetime.now()
        
        for i in range(quantidade):
            try:
                # Gera datas aleatórias para o evento (próximos 30 dias)
                dias_ate_evento = random.randint(1, 30)
                hora_inicio = random.randint(8, 18)  # Entre 8h e 18h
                minutos_inicio = random.choice([0, 15, 30, 45])
                
                start_time = hoje + timedelta(days=dias_ate_evento)
                start_time = start_time.replace(
                    hour=hora_inicio, 
                    minute=minutos_inicio, 
                    second=0, 
                    microsecond=0
                )
                
                # Duração do evento (1 a 4 horas)
                duracao = random.randint(1, 4)
                end_time = start_time + timedelta(hours=duracao)
                
                # Escolhe dados aleatórios para o evento
                titulo = random.choice(titulos)
                descricao = random.choice(descricoes)
                local = random.choice(locais)
                palestrante = random.choice(palestrantes)
                tag = random.choice(tags)
                
                # Decide se o evento é importante (20% de chance)
                importante = random.random() < 0.2
                
                # Gera coordenadas aleatórias (50% de chance de ter coordenadas)
                latitude, longitude = (None, None)
                if random.random() < 0.5:
                    latitude, longitude = self.gerar_coordenadas()
                
                # Cria o evento
                evento = Event.objects.create(
                    titulo=titulo,
                    descricao=descricao,
                    local=local,
                    palestrante=palestrante,
                    start_time=start_time,
                    end_time=end_time,
                    tags=tag,
                    importante=importante,
                    latitude=latitude,
                    longitude=longitude,
                    created_by=usuario
                )
                
                # Gera um número aleatório de favoritos (0 a 100)
                num_favoritos = random.randint(0, 100)
                
                # Se houver favoritos para criar, busca usuários aleatórios
                if num_favoritos > 0:
                    usuarios = list(User.objects.filter(is_active=True))
                    
                    # Se não tiver usuários suficientes, usa o máximo possível
                    if usuarios:
                        # Limita ao número de usuários disponíveis
                        num_favoritos = min(num_favoritos, len(usuarios))
                        
                        # Seleciona usuários aleatórios
                        usuarios_selecionados = random.sample(usuarios, num_favoritos)
                        
                        # Cria os favoritos
                        from apps.agenda.models import UserAgenda
                        for user in usuarios_selecionados:
                            UserAgenda.objects.get_or_create(
                                user=user,
                                event=evento
                            )
                
                eventos_criados += 1
                self.stdout.write(f"Evento criado: {evento.titulo} em {evento.start_time} ({num_favoritos} favoritos)")
                
            except Exception as e:
                self.stderr.write(f"Erro ao criar evento {i+1}: {e}")
                continue
        
        self.stdout.write(
            self.style.SUCCESS(f'\nTotal de eventos criados com sucesso: {eventos_criados}/{quantidade}')
        )
        
        # Mostra estatísticas de favoritos
        from apps.agenda.models import UserAgenda
        total_favoritos = UserAgenda.objects.count()
        eventos_com_favoritos = Event.objects.annotate(
            num_favoritos=models.Count('agenda_usuarios')
        ).filter(num_favoritos__gt=0).count()
        
        self.stdout.write(
            self.style.SUCCESS(f'\n📊 Estatísticas de Favoritos:')
        )
        self.stdout.write(f'   • Total de favoritos criados: {total_favoritos}')
        self.stdout.write(f'   • Eventos com favoritos: {eventos_com_favoritos}')
        
        if eventos_com_favoritos > 0:
            # Mostra top 5 eventos mais favoritados
            top_eventos = Event.objects.annotate(
                num_favoritos=models.Count('agenda_usuarios')
            ).filter(num_favoritos__gt=0).order_by('-num_favoritos')[:5]
            
            self.stdout.write(f'\n🏆 Top 5 Eventos Mais Favoritados:')
            for i, evento in enumerate(top_eventos, 1):
                self.stdout.write(f'   {i}. {evento.titulo}: {evento.num_favoritos} favoritos')

    def handle(self, *args, **options):
        quantidade = options['quantidade']
        self.stdout.write(self.style.SUCCESS(f'Iniciando a criação de {quantidade} eventos de teste...\n'))
        self.criar_eventos_teste(quantidade)
