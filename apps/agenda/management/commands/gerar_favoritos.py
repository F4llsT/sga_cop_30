from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import models
from apps.agenda.models import Event, UserAgenda
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Gera favoritos de eventos para testes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--quantidade',
            type=int,
            default=50,
            help='Número de favoritos a gerar'
        )

    def handle(self, *args, **options):
        quantidade = options['quantidade']
        
        # Pega todos os eventos e usuários
        eventos = list(Event.objects.all())
        usuarios = list(User.objects.filter(is_active=True))
        
        if not eventos:
            self.stdout.write(
                self.style.ERROR('Não há eventos cadastrados. Execute "python manage.py gerar_eventos" primeiro.')
            )
            return
            
        if not usuarios:
            self.stdout.write(
                self.style.ERROR('Não há usuários cadastrados.')
            )
            return
        
        self.stdout.write(f'Gerando {quantidade} favoritos...')
        
        favoritos_criados = 0
        erros = 0
        
        for i in range(quantidade):
            try:
                # Seleciona evento e usuário aleatórios
                evento = random.choice(eventos)
                usuario = random.choice(usuarios)
                
                # Verifica se já não existe
                if not UserAgenda.objects.filter(user=usuario, event=evento).exists():
                    UserAgenda.objects.create(user=usuario, event=evento)
                    favoritos_criados += 1
                    
                    if favoritos_criados % 10 == 0:
                        self.stdout.write(f'  {favoritos_criados} favoritos criados...')
                else:
                    erros += 1
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Erro ao criar favorito: {str(e)}')
                )
                erros += 1
        
        # Mostra estatísticas
        self.stdout.write(
            self.style.SUCCESS(f'\nTotal de favoritos criados: {favoritos_criados}')
        )
        
        if erros > 0:
            self.stdout.write(
                self.style.WARNING(f'Duplicatas ignoradas: {erros}')
            )
        
        # Mostra eventos mais favoritados
        eventos_com_favoritos = (
            Event.objects.annotate(
                num_favoritos=models.Count('agenda_usuarios')
            )
            .filter(num_favoritos__gt=0)
            .order_by('-num_favoritos')[:5]
        )
        
        self.stdout.write('\nTop 5 eventos mais favoritados:')
        for evento in eventos_com_favoritos:
            self.stdout.write(f'  • {evento.titulo}: {evento.num_favoritos} favoritos')
