from django.core.management.base import BaseCommand
from apps.admin_personalizado.models import RedeSocial, Contato, ConfiguracaoSite

class Command(BaseCommand):
    help = 'Configura dados iniciais do site (redes sociais, contatos, configurações)'

    def handle(self, *args, **options):
        self.stdout.write('🔧 Configurando dados iniciais do site...')
        
        # Configurar Redes Sociais
        redes_sociais = [
            {
                'nome': 'Twitter/X',
                'url': 'https://twitter.com/cop30',
                'icone': 'fa-brands fa-x-twitter',
                'ordem': 1
            },
            {
                'nome': 'Instagram',
                'url': 'https://instagram.com/cop30',
                'icone': 'fa-brands fa-instagram',
                'ordem': 2
            },
            {
                'nome': 'LinkedIn',
                'url': 'https://linkedin.com/company/cop30',
                'icone': 'fa-brands fa-linkedin-in',
                'ordem': 3
            },
            {
                'nome': 'Facebook',
                'url': 'https://facebook.com/cop30',
                'icone': 'fa-brands fa-facebook',
                'ordem': 4
            },
            {
                'nome': 'YouTube',
                'url': 'https://youtube.com/cop30',
                'icone': 'fa-brands fa-youtube',
                'ordem': 5
            }
        ]
        
        redes_criadas = 0
        for rede_data in redes_sociais:
            rede, created = RedeSocial.objects.get_or_create(
                nome=rede_data['nome'],
                defaults=rede_data
            )
            if created:
                redes_criadas += 1
                self.stdout.write(f'  ✅ Rede social criada: {rede.nome}')
            else:
                self.stdout.write(f'  📋 Rede social já existe: {rede.nome}')
        
        # Configurar Contatos
        contatos = [
            {
                'tipo_contato': 'Email',
                'valor': 'contato@cop30.com.br',
                'icone': 'fa-solid fa-envelope',
                'ordem': 1
            },
            {
                'tipo_contato': 'Telefone',
                'valor': '(81) 1234-5678',
                'icone': 'fa-solid fa-phone',
                'ordem': 2
            },
            {
                'tipo_contato': 'WhatsApp',
                'valor': '(81) 98765-4321',
                'icone': 'fa-brands fa-whatsapp',
                'ordem': 3
            },
            {
                'tipo_contato': 'Endereço',
                'valor': 'Recife, PE - Brasil',
                'icone': 'fa-solid fa-location-dot',
                'ordem': 4
            }
        ]
        
        contatos_criados = 0
        for contato_data in contatos:
            contato, created = Contato.objects.get_or_create(
                tipo_contato=contato_data['tipo_contato'],
                defaults=contato_data
            )
            if created:
                contatos_criados += 1
                self.stdout.write(f'  ✅ Contato criado: {contato.tipo_contato}')
            else:
                self.stdout.write(f'  📋 Contato já existe: {contato.tipo_contato}')
        
        # Configurar Configurações do Site
        configuracoes = [
            {
                'chave': 'SITE_TITULO',
                'valor': 'COP30 - Conferência das Nações Unidas sobre Mudanças Climáticas',
                'descricao': 'Título principal do site'
            },
            {
                'chave': 'SITE_DESCRICAO',
                'valor': 'Sistema de Gestão de Acessos para a COP30',
                'descricao': 'Descrição do site para SEO'
            },
            {
                'chave': 'SITE_KEYWORDS',
                'valor': 'COP30, clima, sustentabilidade, conferência, ONU',
                'descricao': 'Palavras-chave para SEO'
            },
            {
                'chave': 'FOOTER_COPYRIGHT',
                'valor': '&copy; 2025 COP30. Todos os direitos reservados.',
                'descricao': 'Texto de copyright do footer'
            },
            {
                'chave': 'CONTATO_EMAIL',
                'valor': 'contato@cop30.com.br',
                'descricao': 'Email principal de contato'
            }
        ]
        
        configs_criadas = 0
        for config_data in configuracoes:
            config, created = ConfiguracaoSite.objects.get_or_create(
                chave=config_data['chave'],
                defaults=config_data
            )
            if created:
                configs_criadas += 1
                self.stdout.write(f'  ✅ Configuração criada: {config.chave}')
            else:
                self.stdout.write(f'  📋 Configuração já existe: {config.chave}')
        
        # Resumo final
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('📊 Resumo da configuração:'))
        self.stdout.write(f'  • Redes sociais criadas: {redes_criadas}')
        self.stdout.write(f'  • Contatos criados: {contatos_criados}')
        self.stdout.write(f'  • Configurações criadas: {configs_criadas}')
        
        # Totais existentes
        total_redes = RedeSocial.objects.count()
        total_contatos = Contato.objects.count()
        total_configs = ConfiguracaoSite.objects.count()
        
        self.stdout.write(f'\n📈 Totais no banco:')
        self.stdout.write(f'  • Total de redes sociais: {total_redes}')
        self.stdout.write(f'  • Total de contatos: {total_contatos}')
        self.stdout.write(f'  • Total de configurações: {total_configs}')
        
        self.stdout.write(
            self.style.SUCCESS('\n🎉 Configuração do site concluída com sucesso!')
        )
        
        # Orientações
        self.stdout.write(
            self.style.SUCCESS('\n💡 Próximos passos:')
        )
        self.stdout.write('  • Acesse o admin para gerenciar os dados')
        self.stdout.write('  • Atualize o footer para usar os dados dinâmicos')
        self.stdout.write('  • Configure as URLs reais das redes sociais')
