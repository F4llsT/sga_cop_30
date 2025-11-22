from django.core.management.base import BaseCommand
import random
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from apps.agenda.models import Event

class Command(BaseCommand):
    help = 'Gera eventos de teste para o sistema de agenda'

    def add_arguments(self, parser):
        parser.add_argument('quantidade', type=int, nargs='?', default=10, 
                          help='Número de eventos a serem criados (padrão: 10)')

    def handle(self, *args, **options):
        quantidade = options['quantidade']
        self.gerar_eventos(quantidade)

    def gerar_eventos(self, quantidade):
        # Dados de exemplo para geração de eventos
        titulos = [
            "Workshop de Sustentabilidade",
            "Palestra sobre Energias Renováveis",
            "Oficina de Reciclagem Criativa",
            "Seminário de Desenvolvimento Sustentável",
            "Feira de Tecnologias Verdes",
            "Curso de Agricultura Urbana",
            "Encontro de Empreendedorismo Sustentável",
            "Conferência sobre Mudanças Climáticas",
            "Workshop de Construção Sustentável",
            "Roda de Conversa sobre Consumo Consciente"
        ]

        descricoes = [
            "Um evento incrível para aprender sobre práticas sustentáveis no dia a dia.",
            "Venha conhecer as últimas tendências em sustentabilidade e meio ambiente.",
            "Aprenda a transformar resíduos em produtos incríveis e úteis.",
            "Conheça projetos inovadores que estão mudando o mundo para melhor.",
            "Um espaço para discutir e propor soluções para os desafios ambientais atuais.",
            "Aprenda técnicas de cultivo em pequenos espaços e produza seu próprio alimento.",
            "Conheça cases de sucesso de negócios que unem lucro e sustentabilidade.",
            "Especialistas discutem os impactos das mudanças climáticas e possíveis soluções.",
            "Aprenda técnicas de construção que minimizam o impacto ambiental.",
            "Um bate-papo descontraído sobre como consumir de forma mais consciente."
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

        def gerar_coordenadas():
            # Gera coordenadas aleatórias próximas a uma localização central (ex: São Paulo)
            # Latitude: -23.5505 ± 0.1, Longitude: -46.6333 ± 0.1
            latitude = round(-23.5505 + random.uniform(-0.1, 0.1), 6)
            longitude = round(-46.6333 + random.uniform(-0.1, 0.1), 6)
            return latitude, longitude

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
            self.stderr.write(self.style.ERROR(f'Erro ao obter/criar usuário: {e}'))
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
                    latitude, longitude = gerar_coordenadas()
                
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
                
                eventos_criados += 1
                self.stdout.write(self.style.SUCCESS(f'Evento criado: {evento.titulo} em {evento.start_time}'))
                
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'Erro ao criar evento {i+1}: {e}'))
                continue
        
        self.stdout.write(
            self.style.SUCCESS(f'\nTotal de eventos criados com sucesso: {eventos_criados}/{quantidade}'))
        self.stdout.write(
            self.style.SUCCESS('Acesse a área administrativa para visualizar os eventos: /admin/agenda/event/'))
