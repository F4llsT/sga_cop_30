from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.agenda.models import Event, UserAgenda
from django.db import transaction

User = get_user_model()

class Command(BaseCommand):
    help = 'Apaga todos os eventos e seus favoritos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirmar',
            action='store_true',
            help='Confirma a exclusão sem pedir confirmação'
        )
        parser.add_argument(
            '--favoritos-apenas',
            action='store_true',
            help='Apaga apenas os favoritos, mantendo os eventos'
        )

    def handle(self, *args, **options):
        confirmar = options['confirmar']
        favoritos_apenas = options['favoritos_apenas']
        
        # Contadores
        total_eventos = Event.objects.count()
        total_favoritos = UserAgenda.objects.count()
        
        if favoritos_apenas:
            self.stdout.write(
                self.style.WARNING(f'⚠️  Você está prestes a apagar TODOS os {total_favoritos} favoritos de eventos!')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'⚠️  Você está prestes a apagar:')
            )
            self.stdout.write(f'   • {total_eventos} eventos')
            self.stdout.write(f'   • {total_favoritos} favoritos associados')
        
        if not confirmar:
            confirmacao = input('\nDigite "SIM" para confirmar a exclusão: ')
            if confirmacao != 'SIM':
                self.stdout.write(self.style.ERROR('❌ Operação cancelada.'))
                return
        
        try:
            with transaction.atomic():
                if favoritos_apenas:
                    # Apaga apenas os favoritos
                    UserAgenda.objects.all().delete()
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ {total_favoritos} favoritos apagados com sucesso!')
                    )
                else:
                    # Apaga primeiro os favoritos (devido à foreign key)
                    favoritos_apagados = UserAgenda.objects.count()
                    UserAgenda.objects.all().delete()
                    
                    # Depois apaga os eventos
                    eventos_apagados = Event.objects.count()
                    Event.objects.all().delete()
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ {eventos_apagados} eventos apagados com sucesso!')
                    )
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ {favoritos_apagados} favoritos apagados com sucesso!')
                    )
                    
                    # Mostra resumo
                    self.stdout.write(
                        self.style.SUCCESS(f'\n📋 Resumo da Operação:')
                    )
                    self.stdout.write(f'   • Eventos removidos: {eventos_apagados}')
                    self.stdout.write(f'   • Favoritos removidos: {favoritos_apagados}')
                    self.stdout.write(f'   • Total de registros afetados: {eventos_apagados + favoritos_apagados}')
                    
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erro ao apagar eventos: {str(e)}')
            )
            return
        
        # Verifica se tudo foi apagado
        eventos_restantes = Event.objects.count()
        favoritos_restantes = UserAgenda.objects.count()
        
        if eventos_restantes == 0 and favoritos_restantes == 0:
            self.stdout.write(
                self.style.SUCCESS('🎉 Todos os eventos e favoritos foram removidos com sucesso!')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'⚠️  Ainda restam {eventos_restantes} eventos e {favoritos_restantes} favoritos')
            )
