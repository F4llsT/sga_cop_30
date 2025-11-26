from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from apps.passefacil.models import PasseFacil

User = get_user_model()

class Command(BaseCommand):
    help = 'Apaga Passe Fácil de usuários específicos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirmar',
            action='store_true',
            help='Confirma a exclusão sem pedir confirmação'
        )
        parser.add_argument(
            '--usuarios-inativos',
            action='store_true',
            help='Apaga apenas de usuários inativos (is_active=False)'
        )
        parser.add_argument(
            '--staff',
            action='store_true',
            help='Apaga apenas de usuários staff (is_staff=True)'
        )
        parser.add_argument(
            '--todos',
            action='store_true',
            help='Apaga TODOS os Passe Fácil (CUIDADO!)'
        )

    def handle(self, *args, **options):
        confirmar = options['confirmar']
        usuarios_inativos = options['usuarios_inativos']
        staff = options['staff']
        todos = options['todos']
        
        # Query base
        passes_query = PasseFacil.objects.select_related('user')
        
        # Aplicar filtros
        if usuarios_inativos:
            passes_query = passes_query.filter(user__is_active=False)
        elif staff:
            passes_query = passes_query.filter(user__is_staff=True)
        elif not todos:
            # Se não especificou, apaga apenas de usuários não-staff ativos
            passes_query = passes_query.filter(user__is_active=True, user__is_staff=False)
        
        total_passes = PasseFacil.objects.count()
        passes_para_apagar = passes_query.count()
        
        if passes_para_apagar == 0:
            self.stdout.write(
                self.style.WARNING('⚠️  Nenhum Passe Fácil encontrado para os critérios especificados')
            )
            self.stdout.write(f'   • Total de passes no sistema: {total_passes}')
            return
        
        # Mostrar informações
        self.stdout.write(
            self.style.WARNING(f'⚠️  Você está prestes a apagar {passes_para_apagar} Passe Fácil')
        )
        self.stdout.write(f'   • Total de passes no sistema: {total_passes}')
        self.stdout.write(f'   • Passes que serão apagados: {passes_para_apagar}')
        
        # Mostrar exemplos
        exemplos = passes_query[:5]
        if exemplos:
            self.stdout.write(f'\n📝 Exemplos de passes que serão apagados:')
            for passe in exemplos:
                nome = (getattr(passe.user, 'get_full_name', lambda: None)() or 
                       getattr(passe.user, 'nome', None) or 
                       getattr(passe.user, 'username', 'Usuário'))
                self.stdout.write(f'   • {nome}: {passe.codigo}')
        
        if passes_para_apagar > 5:
            self.stdout.write(f'   ... e mais {passes_para_apagar - 5} passes')
        
        if not confirmar:
            if todos:
                self.stdout.write(f'\n🚨 ATENÇÃO: Você está apagando TODOS os Passe Fácil!')
                confirmacao = input(f'\n❓ Digite "APAGAR_TUDO" para confirmar: ')
                if confirmacao != 'APAGAR_TUDO':
                    self.stdout.write(self.style.ERROR('❌ Operação cancelada.'))
                    return
            else:
                confirmacao = input(f'\n❓ Deseja apagar {passes_para_apagar} Passe Fácil? (SIM/NÃO): ')
                if confirmacao != 'SIM':
                    self.stdout.write(self.style.ERROR('❌ Operação cancelada.'))
                    return
        
        # Apagar passes
        self.stdout.write(f'\n🗑️  Apagando {passes_para_apagar} Passe Fácil...')
        
        apagados = 0
        erros = 0
        
        with transaction.atomic():
            for passe in passes_query:
                try:
                    nome = (getattr(passe.user, 'get_full_name', lambda: None)() or 
                           getattr(passe.user, 'nome', None) or 
                           getattr(passe.user, 'username', 'Usuário'))
                    passe.delete()
                    apagados += 1
                    
                    if apagados % 10 == 0:
                        self.stdout.write(f'  🗑️  {apagados} passes apagados...')
                    
                except Exception as e:
                    self.stderr.write(f'❌ Erro ao apagar Passe Fácil de {nome}: {str(e)}')
                    erros += 1
                    continue
        
        # Relatório final
        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 Operação concluída!')
        )
        self.stdout.write(f'   • Passes apagados: {apagados}')
        
        if erros > 0:
            self.stdout.write(
                self.style.WARNING(f'   • Erros: {erros}')
            )
        
        # Verificação final
        total_final = PasseFacil.objects.count()
        self.stdout.write(
            self.style.SUCCESS(f'\n📈 Estatísticas finais:')
        )
        self.stdout.write(f'   • Passe Fácil restantes: {total_final}')
        self.stdout.write(f'   • Taxa de cobertura: {(total_final / User.objects.count() * 100):.1f}%')
        
        # Orientações
        self.stdout.write(
            self.style.SUCCESS(f'\n💡 Próximos passos:')
        )
        self.stdout.write(f'   • Para recriar passes: python manage.py criar_passe_facil_todos')
        self.stdout.write(f'   • Para verificar passes: /meu-admin/passe-facil/')
        
        if apagados == passes_para_apagar:
            self.stdout.write(
                self.style.SUCCESS(f'\n🎯 SUCESSO: Todos os passes selecionados foram removidos!')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'\n⚠️  Alguns passes não puderam ser apagados. Verifique os erros acima.')
            )
