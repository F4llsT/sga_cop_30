# 🌍 SGA COP 30

Sistema de Gestão de Acessos para a Conferência das Nações Unidas sobre Mudanças Climáticas (COP30).

## 📋 Visão Geral

O SGA COP 30 é uma plataforma completa para gerenciamento de eventos, usuários, acessos e notificações da COP30. Desenvolvido com Django, oferece um dashboard administrativo robusto, sistema de passes (Passe Fácil), gestão de eventos e notificações inteligentes.

## ✨ Funcionalidades Principais

### 🎫 Passe Fácil
- **Geração de passes**: UUID únicos para cada usuário
- **QR Codes**: Interface visual para validação
- **Timer 60s**: Tempo restante para validação
- **Histórico completo**: Registro de todas as tentativas
- **Dashboard admin**: Gerenciamento completo

### 📅 Sistema de Eventos
- **Criação de eventos**: Título, descrição, local, data
- **Sistema de favoritos**: Usuários podem favoritar eventos
- **Dashboard interativo**: Estatísticas em tempo real
- **API REST**: Endpoint para integrações

### 📢 Notificações Inteligentes
- **Mensagens personalizadas**: info, success, warning, error
- **Controle de leitura**: Timestamps precisos
- **Avisos globais**: Níveis de importância
- **Limpeza automática**: Expiração por tempo

### 👥 Gestão de Usuários
- **Model personalizado**: Campo `nome` em vez de `username`
- **Perfis variados**: Admin, staff, usuários comuns
- **Dados de teste**: Geração em massa para desenvolvimento

## 🚀 Quick Start

### Pré-requisitos
- Python 3.8+
- PostgreSQL
- Redis (opcional, para cache)

### Instalação

1. **Clone o repositório:**
```bash
git clone <repository-url>
cd sga_cop_30
```

2. **Ambiente virtual:**
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows
```

3. **Dependências:**
```bash
pip install -r requirements.txt
```

4. **Configurar banco:**
```bash
# Editar settings.py com suas credenciais PostgreSQL
```

5. **Migrações:**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Superusuário:**
```bash
python manage.py createsuperuser
```

7. Dados de teste:
```bash
python manage.py criar_usuarios_teste --quantidade 100
python manage.py gerar_eventos --quantidade 10
python manage.py criar_passe_facil_todos --confirmar
python manage.py gerar_validacoes_teste --quantidade 200 --dias-atras 365
python manage.py criar_notificacoes_exemplo
python manage.py criar_avisos_coop30 10
```

8. Configurar dados iniciais do site:
```bash
python manage.py configurar_site
```

9. Iniciar servidor:
```bash
python manage.py runserver
```

## Acessos

### Interfaces Web
- **Dashboard Admin**: `http://127.0.0.1:8000/meu-admin/dashboard/`
- **Passe Fácil Admin**: `http://127.0.0.1:8000/meu-admin/passe-facil/`
- **Passe Fácil Usuário**: `http://127.0.0.1:8000/passefacil/`

### API REST
- **Eventos**: `GET /meu-admin/api/eventos/`
- **Avisos**: `GET /meu-admin/api/avisos/`
- **Usuários**: `GET /meu-admin/api/usuarios/`

## 🛠️ Comandos Management

### Usuários
```bash
# Criar usuários de teste
python manage.py criar_usuarios_teste --quantidade 100

# Apagar usuários de teste
python manage.py apagar_usuarios_teste --confirmar
```

### Eventos
```bash
# Gerar eventos com favoritos
python manage.py gerar_eventos --quantidade 20

# Gerar apenas favoritos
python manage.py gerar_favoritos --quantidade 100

# Apagar eventos
python manage.py apagar_eventos --confirmar
```

### Passe Fácil
```bash
# Criar passes para todos
python manage.py criar_passe_facil_todos --confirmar

# Apenas usuários ativos
python manage.py criar_passe_facil_todos --usuarios-ativos

# Apagar passes
python manage.py apagar_passe_facil --usuarios-inativos
```

### Validações
```bash
# Gerar dados históricos
python manage.py gerar_validacoes_teste --quantidade 500 --dias-atras 365

# Taxa de sucesso personalizada
python manage.py gerar_validacoes_teste --taxa-sucesso 0.95

# Limpar validações
python manage.py apagar_validacoes_teste --confirmar
```

### Notificações
```bash
# Verificar notificações
python manage.py check_notifications --nao-lidas

# Limpeza automática
python manage.py cleanup_notifications --dry-run

# Criar avisos COOP30
python manage.py criar_avisos_coop30 15

# Criar notificações de exemplo
python manage.py criar_notificacoes_exemplo

# Enviar notificações pendentes
python manage.py send_notifications
```

### Configuração do Site
```bash
# Configurar dados iniciais (redes sociais, contatos, configurações)
python manage.py configurar_site
```

**O que este comando faz:**
- **Redes Sociais**: Cria X/Twitter, Instagram, LinkedIn, Facebook, YouTube
- **Contatos**: Configura Email, Telefone, WhatsApp, Endereço
- **Configurações**: Define título, descrição, keywords, copyright do site

**Dados criados:**
- 5 redes sociais com ícones Font Awesome
- 4 tipos de contato com informações padrão
- 5 configurações básicas do site

**Uso recomendado:**
- Executar após as migrações iniciais
- Executar novamente para resetar dados padrão
- Safe para execução múltipla (não duplica dados)

## 📊 Estrutura do Projeto

```
sga_cop_30/
├── apps/
│   ├── agenda/           # Sistema de eventos
│   ├── passefacil/       # Passe Fácil e validações
│   ├── notificacoes/     # Sistema de notificações
│   ├── admin_personalizado/  # Dashboard admin
│   └── usuarios/         # Gestão de usuários
├── static/               # Arquivos estáticos
├── templates/            # Templates HTML
├── manage.py            # Django management
└── requirements.txt     # Dependências
```

## 🗄️ Models Principais

### Event
- Título, descrição, local, data
- Sistema de favoritos
- API endpoints

### PasseFacil
- Relacionamento OneToOne com User
- UUID único para validação
- Timer de 60 segundos
- Histórico de validações

### ValidacaoQRCode
- Registro de tentativas
- Data, IP, status
- Análise temporal

### Notificacao
- Mensagens para usuários
- Tipos variados (info, success, warning, error)
- Controle de leitura

### Aviso
- Avisos globais
- Níveis de importância
- Expiração automática

## 🔧 Configuração

### Settings Principais
```python
# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'cop30_db',
        'USER': 'cop30_user',
        'PASSWORD': 'senha',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Timezone
TIME_ZONE = 'America/Sao_Paulo'
USE_TZ = True

# Apps instalados
INSTALLED_APPS = [
    # ... apps django
    'apps.agenda',
    'apps.passefacil',
    'apps.notificacoes',
    'apps.admin_personalizado',
    'apps.usuarios',
]
```

## 📱 API REST

### Endpoints

#### Eventos
```http
GET /meu-admin/api/eventos/
Content-Type: application/json

Response:
[
    {
        "id": 1,
        "titulo": "Sustentabilidade e Meio Ambiente",
        "descricao": "Discussão sobre práticas sustentáveis",
        "local": "Auditório Principal",
        "data_evento": "2025-11-30T14:00:00Z",
        "ativo": true,
        "num_favoritos": 25,
        "favoritado": true
    }
]
```

#### Avisos
```http
GET /meu-admin/api/avisos/
Content-Type: application/json

Response:
[
    {
        "id": 1,
        "titulo": "Atualização do Regimento",
        "mensagem": "Nova versão disponível",
        "nivel": "info",
        "data_criacao": "2025-11-26T10:00:00Z",
        "fixo_no_topo": true,
        "ativo": true
    }
]
```

## 🧪 Testes e Dados

### Gerar Ambiente Completo
```bash
# Setup completo para desenvolvimento
python manage.py apagar_eventos --confirmar
python manage.py apagar_usuarios_teste --confirmar
python manage.py apagar_passe_facil --todos --confirmar
python manage.py apagar_validacoes_teste --confirmar

python manage.py criar_usuarios_teste --quantidade 50
python manage.py gerar_eventos --quantidade 20
python manage.py criar_passe_facil_todos --confirmar
python manage.py gerar_validacoes_teste --quantidade 100 --dias-atras 90
python manage.py criar_notificacoes_exemplo
python manage.py criar_avisos_coop30 10
```

## 🔍 Debug

### Verificar Funcionalidades
```bash
# Dashboard de eventos
python manage.py shell
>>> from apps.agenda.models import Event, UserAgenda
>>> Event.objects.annotate(num_fav=Count('agenda_usuarios')).filter(num_fav__gt=0).count()

# Passe Fácil
>>> from apps.passefacil.models import PasseFacil, ValidacaoQRCode
>>> PasseFacil.objects.count()
>>> ValidacaoQRCode.objects.count()

# Notificações
>>> from apps.notificacoes.models import Notificacao, NotificacaoUsuario
>>> NotificacaoUsuario.objects.filter(lida=False).count()
```

## 📈 Performance

### Otimizações Implementadas
- **select_related**: Reduz queries N+1
- **annotate**: Agregações eficientes
- **indexes**: Índices em campos pesquisados
- **cache**: Cache para dashboard (configurável)

### Monitoramento
```python
# Verificar queries
python manage.py shell --settings=settings.debug

# Logs de performance
DEBUG=True em settings.py
```

## 🤝 Contribuição

1. Fork o projeto
2. Create branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit changes (`git commit -am 'Add nova funcionalidade'`)
4. Push to branch (`git push origin feature/nova-funcionalidade`)
5. Create Pull Request

## 📝 Licença

Este projeto é licenciado sob a MIT License.

## 📞 Suporte

- **Documentação completa**: `DOCUMENTACAO.md`
- **Issues**: GitHub Issues
- **Email**: suporte@cop30.com

---

**Desenvolvido para a COP30** 🌍♻️

**Versão**: 1.0.0  
**Última atualização**: 26/11/2025