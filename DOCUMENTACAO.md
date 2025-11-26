# Documentação do Sistema COP30 - Dashboard de Eventos e Favoritos

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Estrutura do Sistema](#estrutura-do-sistema)
3. [Comandos de Management](#comandos-de-management)
4. [Views e URLs](#views-e-urls)
5. [Models e Serializers](#models-e-serializers)
6. [Templates e Frontend](#templates-e-frontend)
7. [Funcionalidades Implementadas](#funcionalidades-implementadas)
8. [Como Usar](#como-usar)
9. [Troubleshooting](#troubleshooting)

---

## 🎯 Visão Geral

Este projeto implementa um **dashboard administrativo para eventos da COP30** com funcionalidades de:

- **Gestão de Eventos**: Criar, editar, excluir eventos
- **Sistema de Favoritos**: Usuários podem favoritar eventos
- **Dashboard Analítico**: Estatísticas e visualizações
- **Gestão de Usuários**: Sistema completo de administração

### Tecnologias Utilizadas
- **Backend**: Django 5.2.6 + Django REST Framework
- **Frontend**: Bootstrap 5, DataTables, Leaflet.js, Select2
- **Banco**: PostgreSQL (configurável)
- **Autenticação**: Sistema personalizado de usuários

---

## 🏗️ Estrutura do Sistema

```
sga_cop_30/
├── apps/
│   ├── agenda/                    # Módulo de eventos
│   │   ├── models.py             # Model Event e UserAgenda
│   │   ├── serializers.py        # EventSerializer
│   │   └── management/
│   │       └── commands/
│   │           ├── gerar_eventos.py
│   │           ├── apagar_eventos.py
│   │           └── gerar_favoritos.py
│   ├── admin_personalizado/       # Dashboard admin
│   │   ├── views.py              # Views principais
│   │   ├── urls.py               # URLs do admin
│   │   └── templates/
│   │       └── admin_personalizado/
│   │           ├── dashboard/
│   │           └── evento/
│   └── usuarios/                 # Sistema de usuários
│       └── management/
│           └── commands/
│               ├── criar_usuarios_teste.py
│               └── apagar_usuarios_teste.py
├── static/
│   └── admin_personalizado/
│       ├── js/
│       └── css/
└── templates/
    └── admin_personalizado/
        └── baseadmin.html
```

---

## 🛠️ Comandos de Management

### 📅 Eventos

#### `gerar_eventos.py`
Cria eventos de teste com favoritos aleatórios.

```bash
# Uso básico (10 eventos)
python manage.py gerar_eventos

# Quantidade personalizada
python manage.py gerar_eventos --quantidade 50
```

**Funcionalidades:**
- Gera eventos com datas aleatórias (próximos 30 dias)
- Cria entre 0-100 favoritos por evento
- Usa usuários existentes para favoritos
- Gera coordenadas aleatórias (50% de chance)
- 20% de chance de ser evento importante

#### `apagar_eventos.py`
Remove todos os eventos e favoritos.

```bash
# Apagar com confirmação
python manage.py apagar_eventos

# Apagar sem confirmação
python manage.py apagar_eventos --confirmar

# Apagar apenas favoritos
python manage.py apagar_eventos --favoritos-apenas
```

#### `gerar_favoritos.py`
Cria favoritos para eventos existentes.

```bash
# Criar 50 favoritos aleatórios
python manage.py gerar_favoritos --quantidade 50
```

### 🎫 Passe Fácil

#### `criar_passe_facil_todos.py`
Cria Passe Fácil para todos os usuários que ainda não possuem.

```bash
# Criar para todos (com confirmação)
python manage.py criar_passe_facil_todos

# Sem confirmação
python manage.py criar_passe_facil_todos --confirmar

# Apenas usuários ativos
python manage.py criar_passe_facil_todos --usuarios-ativos

# Ignorando staff
python manage.py criar_passe_facil_todos --ignorar-staff
```

**Funcionalidades:**
- Cria passes para usuários sem Passe Fácil
- Gera UUID único para cada passe
- Relatórios detalhados de criação
- Filtros por status e tipo de usuário
- Verificação de duplicatas

#### `apagar_passe_facil.py`
Remove Passe Fácil de usuários com base em critérios.

```bash
# Apagar de usuários não-staff ativos
python manage.py apagar_passe_facil

# Apagar de usuários inativos
python manage.py apagar_passe_facil --usuarios-inativos

# Apagar apenas de staff
python manage.py apagar_passe_facil --staff

# APAGAR TODOS (cuidado!)
python manage.py apagar_passe_facil --todos
```

**Funcionalidades:**
- Apaga passes seletivamente
- Confirmação de segurança para operações destrutivas
- Relatórios de passes removidos
- Verificação final de cobertura

#### `gerar_validacoes_teste.py`
Cria validações de Passe Fácil com usuários e datas aleatórias.

```bash
# Criar 100 validações nos últimos 120 dias
python manage.py gerar_validacoes_teste

# Quantidade personalizada
python manage.py gerar_validacoes_teste --quantidade 500

# Período personalizado
python manage.py gerar_validacoes_teste --dias-atras 365

# Taxa de sucesso personalizada
python manage.py gerar_validacoes_teste --taxa-sucesso 0.95

# Sem confirmação
python manage.py gerar_validacoes_teste --confirmar
```

**Funcionalidades:**
- Gera datas aleatórias distribuídas no período
- Taxa de sucesso configurável (padrão 85%)
- IPs variados para simular acessos reais
- Relatórios detalhados de criação
- Debug de datas para verificação

#### `apagar_validacoes_teste.py`
Remove validações de Passe Fácil de teste.

```bash
# Apagar tudo (com confirmação)
python manage.py apagar_validacoes_teste

# Apagar tudo (sem confirmação)
python manage.py apagar_validacoes_teste --confirmar

# Apagar apenas recentes
python manage.py apagar_validacoes_teste --dias-recentes 7

# Apagar último mês
python manage.py apagar_validacoes_teste --dias-recentes 30
```

**Funcionalidades:**
- Apaga todas as validações ou por período
- Preview das validações mais recentes
- Confirmação segura com "APAGAR TUDO"
- Estatísticas detalhadas da operação
- Transação atômica para segurança

### 📢 Notificações

#### `check_notifications.py`
Verifica e exibe estatísticas das notificações dos usuários.

```bash
# Verificar todas as notificações
python manage.py check_notifications

# Filtrar por email
python manage.py check_notifications --email admin@cop30.com

# Apenas não lidas
python manage.py check_notifications --nao-lidas

# Combinar filtros
python manage.py check_notifications --email cop30 --nao-lidas
```

**Funcionalidades:**
- Estatísticas por usuário
- Filtros por email e status
- Últimas notificações detalhadas
- Status de leitura com timestamps
- Relatório completo de uso

#### `cleanup_notifications.py`
Remove notificações expiradas ou antigas do banco de dados.

```bash
# Limpar notificações expiradas
python manage.py cleanup_notifications

# Modo de teste (não apaga)
python manage.py cleanup_notifications --dry-run
```

**Funcionalidades:**
- Remove lidas (1h após leitura)
- Remove não lidas (10 dias após criação)
- Remove com expiração manual
- Modo dry-run seguro
- Relatório de remoções

#### `criar_avisos_coop30.py`
Cria avisos de exemplo relacionados à COOP 30.

```bash
# Criar 5 avisos (padrão)
python manage.py criar_avisos_coop30

# Quantidade personalizada
python manage.py criar_avisos_coop30 10
```

**Funcionalidades:**
- Avisos temáticos COOP 30
- Níveis de importância variados
- Datas de expiração aleatórias
- Fixo no topo opcional
- 75% ativos por padrão

#### `criar_notificacoes_exemplo.py`
Cria notificações de exemplo para demonstração.

```bash
# Criar notificações para todos os usuários
python manage.py criar_notificacoes_exemplo
```

**Funcionalidades:**
- 5 tipos de notificações padrão
- Cria admin@cop30.com se necessário
- Limpa notificações existentes
- Diversos níveis (info, success, warning, error)
- Estatísticas detalhadas

#### `send_notifications.py`
Envia notificações pendentes para os usuários (framework para envio).

```bash
# Processar todas as notificações não lidas
python manage.py send_notifications
```

**Funcionalidades:**
- Processa todas as notificações não lidas
- Framework para envio por email/push
- Tratamento de erros individual
- Relatório de processamento
- Extensível para outros canais

**Observação:** Este comando serve como base para implementação de envio real (email, SMS, push notifications).

### 👥 Usuários

#### `criar_usuarios_teste.py`
Cria usuários de teste para o sistema.

```bash
# Criar 10 usuários (padrão)
python manage.py criar_usuarios_teste

# Quantidade personalizada
python manage.py criar_usuarios_teste --quantidade 100

# Prefixo personalizado
python manage.py criar_usuarios_teste --prefixo demo --quantidade 50
```

**Características:**
- Usa campo `nome` (modelo personalizado)
- Senha padrão: `senha123`
- Não preenche `first_name` e `last_name`
- Gera emails aleatórios

#### `apagar_usuarios_teste.py`
Remove apenas usuários de teste.

```bash
# Apagar usuários com prefixo "teste"
python manage.py apagar_usuarios_teste

# Prefixo específico
python manage.py apagar_usuarios_teste --prefixo demo

# Sem confirmação
python manage.py apagar_usuarios_teste --confirmar
```

---

## 🌐 Views e URLs

### Dashboard Principal

#### `views.dashboard`
**URL**: `/meu-admin/dashboard/`

**Funcionalidades:**
- Métricas de usuários e eventos
- Gráfico de eventos mais favoritados
- Tabela com top 10 eventos favoritados
- Filtros por período (hoje, 7d, 30d)

**Dados Context:**
```python
context = {
    "summary": {
        "total_users": total_users,
        "active_today": active_today,
        "total_events": Event.objects.count(),
        "passe_uses": passe_uses,
        "top_event": top_event,
    },
    "eventos_com_favoritos": eventos_com_favoritos,
    "eventos_labels": eventos_labels,
    "eventos_values": eventos_values,
}
```

#### `views.criar_favoritos_teste`
**URL**: `/meu-admin/criar-favoritos-teste/`

Cria favoritos aleatórios para testes via interface web.

### API de Eventos

#### `views.api_eventos`
**URL**: `/meu-admin/api/eventos/`

**Métodos:**
- `GET`: Lista eventos com paginação
- `POST`: Cria novo evento

**Features:**
- Paginação com `Paginator`
- Filtros (busca, datas, importância)
- Usa `Event.all_objects` (sem filtro)
- Serialização com `EventSerializer`

#### CRUD de Eventos
- `views.evento_criar`: `/meu-admin/eventos/novo/`
- `views.evento_editar`: `/meu-admin/eventos/<id>/editar/`
- `views.evento_excluir`: `/meu-admin/eventos/<id>/excluir/`
- `views.api_evento_detalhe`: `/meu-admin/api/eventos/<id>/`

---

## 📊 Models e Serializers

### Models

#### `Event`
```python
class Event(models.Model):
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    local = models.CharField(max_length=200, blank=True)
    palestrante = models.CharField(max_length=200, blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    tags = models.CharField(max_length=500, blank=True)
    importante = models.BooleanField(default=False)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = EventManager()  # Manager padrão (sem filtro)
    all_objects = models.Manager()  # Manager para todos os eventos
```

#### `UserAgenda` (Favoritos)
```python
class UserAgenda(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='agenda_pessoal')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='agenda_usuarios')
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'event')  # Evita duplicatas
```

#### `PasseFacil`
```python
class PasseFacil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='passe_facil')
    codigo = models.UUIDField(default=uuid.uuid4, editable=False)
    secret_totp = models.CharField(max_length=100, null=True, blank=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    ultima_geracao = models.DateTimeField(null=True, blank=True)
    ativo = models.BooleanField(default=True)
    tentativas_validacao = models.PositiveIntegerField(default=0)
    ultima_tentativa = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Passe Fácil - {self.user.get_full_name() or self.user.username}"
    
    @property
    def tempo_restante(self):
        tempo_decorrido = timezone.now() - self.data_atualizacao
        return max(60 - int(tempo_decorrido.total_seconds()), 0)
    
    def gerar_novo_codigo(self):
        self.codigo = uuid.uuid4()
        self.data_atualizacao = timezone.now()
        self.save()
```

#### `ValidacaoQRCode`
```python
class ValidacaoQRCode(models.Model):
    passe_facil = models.ForeignKey(PasseFacil, on_delete=models.CASCADE, related_name='validacoes')
    codigo = models.CharField(max_length=36)
    data_validacao = models.DateTimeField(default=timezone.now)
    valido = models.BooleanField(default=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-data_validacao']
        verbose_name = 'Validação de QR Code'
        verbose_name_plural = 'Validações de QR Code'

    def __str__(self):
        status = "Válido" if self.valido else "Inválido"
        return f"Validação {self.id} - {self.passe_facil.user} - {status} - {self.data_validacao}"
```

#### `Notificacao`
```python
class Notificacao(models.Model):
    titulo = models.CharField(max_length=200)
    mensagem = models.TextField()
    tipo = models.CharField(max_length=20, choices=[('info', 'info'), ('success', 'success'), ('warning', 'warning'), ('error', 'error')])
    criado_por = models.ForeignKey(User, on_delete=models.CASCADE)
    criada_em = models.DateTimeField(auto_now_add=True)
    lida = models.BooleanField(default=False)
    lida_em = models.DateTimeField(null=True, blank=True)
    data_expiracao = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-criada_em']
        verbose_name = 'Notificação'
        verbose_name_plural = 'Notificações'

    def __str__(self):
        return f"{self.titulo} - {self.criada_em.strftime('%d/%m/%Y %H:%M')}"
```

#### `NotificacaoUsuario`
```python
class NotificacaoUsuario(models.Model):
    notificacao = models.ForeignKey(Notificacao, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    lida = models.BooleanField(default=False)
    lida_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-notificacao__criada_em']
        unique_together = ['notificacao', 'usuario']
        verbose_name = 'Notificação do Usuário'
        verbose_name_plural = 'Notificações dos Usuários'

    def __str__(self):
        status = "Lida" if self.lida else "Não lida"
        return f"{self.usuario.email} - {self.notificacao.titulo} ({status})"
```

#### `Aviso`
```python
class Aviso(models.Model):
    titulo = models.CharField(max_length=200)
    mensagem = models.TextField()
    nivel = models.CharField(max_length=20, choices=[('info', 'info'), ('alerta', 'alerta'), ('critico', 'critico')])
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_expiracao = models.DateTimeField(null=True, blank=True)
    fixo_no_topo = models.BooleanField(default=False)
    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ['-fixo_no_topo', '-data_criacao']
        verbose_name = 'Aviso'
        verbose_name_plural = 'Avisos'

    def __str__(self):
        return f"{self.titulo} - {self.nivel.upper()}"
```

#### `EventManager`
```python
class EventManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()  # Retorna todos (sem filtro)
    
    def active_events(self):
        # Método separado para eventos ativos (últimas 10 horas)
        ten_hours_ago = timezone.now() - timedelta(hours=10)
        return super().get_queryset().filter(
            Q(start_time__isnull=True) | Q(start_time__gte=ten_hours_ago)
        )
```

### Serializers

#### `EventSerializer`
```python
class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            'id', 'titulo', 'descricao', 'local', 'palestrante',
            'start_time', 'end_time', 'tags', 'importante',
            'latitude', 'longitude', 'created_at'
        ]
    
    def to_representation(self, instance):
        # Formata datas em ISO 8601
        data = super().to_representation(instance)
        if instance.start_time:
            data['start_time'] = instance.start_time.isoformat()
        if instance.end_time:
            data['end_time'] = instance.end_time.isoformat()
        return data
    
    def validate(self, data):
        # Validação de datas e timezone
        if data.get('start_time') and data.get('end_time'):
            if data['end_time'] <= data['start_time']:
                raise serializers.ValidationError("end_time deve ser após start_time")
        return data
```

---

## 🎨 Templates e Frontend

### Dashboard (`dashboard.html`)

**Estrutura principal:**
```html
<section class="summary-section">
    <!-- Cards de métricas -->
</section>

<section class="charts-section">
    <!-- Gráfico + Tabela de favoritos -->
    {% if eventos_com_favoritos %}
    <table class="table table-striped table-hover">
        <thead class="table-dark">
            <tr>
                <th>Evento</th>
                <th>Local</th>
                <th>Data</th>
                <th class="text-center">Favoritos</th>
            </tr>
        </thead>
        <tbody>
            {% for evento in eventos_com_favoritos %}
            <tr>
                <td><strong>{{ evento.titulo }}</strong></td>
                <td>{{ evento.local|default:"—" }}</td>
                <td>{{ evento.start_time|date:"d/m/Y H:i" }}</td>
                <td class="text-center">
                    <span class="badge bg-primary fs-6">
                        <i class="fas fa-star"></i> {{ evento.num_favoritos }}
                    </span>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    {% endif %}
</section>
```

**JavaScript (eventos.js):**
- DataTables para paginação client-side
- Leaflet.js para mapas
- Select2 para selects estilizados
- AJAX para API calls

**CSS (usuario_list.css):**
- Design responsivo
- Variáveis CSS para temas
- Animações e transições
- Paginação estilizada

---

## ⚡ Funcionalidades Implementadas

### 1. Dashboard de Eventos
- ✅ **Cards de métricas**: Usuários, eventos ativos, passe fácil
- ✅ **Gráfico interativo**: Eventos mais favoritados (Chart.js)
- ✅ **Tabela de favoritos**: Top 10 eventos com mais favoritos
- ✅ **Filtros por período**: Hoje, 7 dias, 30 dias
- ✅ **Botão de teste**: Gerar favoritos automaticamente

### 2. Sistema de Favoritos
- ✅ **Model UserAgenda**: Relacionamento N:N entre usuários e eventos
- ✅ **Contagem automática**: `annotate(Count('agenda_usuarios'))`
- ✅ **Filtro inteligente**: Apenas eventos com > 0 favoritos
- ✅ **Ordenação**: Mais favoritados primeiro
- ✅ **Prevenção de duplicatas**: `unique_together`

### 3. API REST
- ✅ **Endpoint listagem**: GET `/api/eventos/`
- ✅ **Endpoint criação**: POST `/api/eventos/`
- ✅ **Endpoint detalhe**: GET `/api/eventos/<id>/`
- ✅ **Paginação**: Django Paginator
- ✅ **Filtros**: Busca, datas, importância
- ✅ **Serialização**: ISO 8601 para datas

### 4. Passe Fácil
- ✅ **Model PasseFacil**: Relacionamento OneToOne com User
- ✅ **UUID único**: Código gerado automaticamente
- ✅ **Timer 60s**: Tempo restante para validação
- ✅ **QR Code**: Interface visual para passes
- ✅ **Admin panel**: Dashboard de gerenciamento
- ✅ **Validações**: Registro de tentativas com IP e data
- ✅ **Dados históricos**: Análise temporal de uso

### 5. Sistema de Notificações
- ✅ **Model Notificacao**: Mensagens para usuários
- ✅ **Model NotificacaoUsuario**: Relacionamento many-to-many
- ✅ **Model Aviso**: Avisos globais com níveis
- ✅ **Tipos variados**: info, success, warning, error
- ✅ **Controle de leitura**: Timestamps e status
- ✅ **Expiração automática**: Limpeza de antigas
- ✅ **Dashboard admin**: Gerenciamento completo

### 6. Comandos de Teste
- ✅ **gerar_eventos**: Eventos + favoritos aleatórios
- ✅ **apagar_eventos**: Limpeza completa
- ✅ **criar_usuarios_teste**: Usuários para testes
- ✅ **apagar_usuarios_teste**: Limpeza segura
- ✅ **criar_passe_facil_todos**: Passe Fácil em massa
- ✅ **apagar_passe_facil**: Remoção seletiva
- ✅ **gerar_validacoes_teste**: Dados históricos realistas
- ✅ **apagar_validacoes_teste**: Limpeza de validações
- ✅ **check_notifications**: Verificação de notificações
- ✅ **cleanup_notifications**: Limpeza automática
- ✅ **criar_avisos_coop30**: Avisos temáticos
- ✅ **criar_notificacoes_exemplo**: Dados demonstrativos
- ✅ **send_notifications**: Framework de envio

---

## 🚀 Como Usar

### Setup Inicial

1. **Criar superusuário:**
```bash
python manage.py createsuperuser
```

2. **Criar dados de teste:**
```bash
# Criar usuários para favoritos
python manage.py criar_usuarios_teste --quantidade 100

# Criar eventos com favoritos
python manage.py gerar_eventos --quantidade 10

# Criar Passe Fácil para todos
python manage.py criar_passe_facil_todos --confirmar

# Gerar validações históricas
python manage.py gerar_validacoes_teste --quantidade 200 --dias-atras 365

# Criar notificações de exemplo
python manage.py criar_notificacoes_exemplo

# Criar avisos COOP 30
python manage.py criar_avisos_coop30 10
```

3. **Iniciar servidor:**
```bash
python manage.py runserver
```

4. **Acessar interfaces:**
```bash
# Dashboard admin
http://127.0.0.1:8000/meu-admin/dashboard/

# Passe Fácil admin
http://127.0.0.1:8000/meu-admin/passe-facil/

# Passe Fácil usuário
http://127.0.0.1:8000/passefacil/
```

### Fluxo de Teste

1. **Acessar dashboard** → Ver métricas iniciais
2. **Gerar eventos** → `python manage.py gerar_eventos 10`
3. **Recarregar dashboard** → Ver tabela de favoritos
4. **Criar evento manual** → Via interface admin
5. **Testar filtros** → Período (7d, 30d)

### Comandos Úteis

```bash
# Limpar tudo e recomeçar
python manage.py apagar_eventos --confirmar
python manage.py apagar_usuarios_teste --confirmar
python manage.py apagar_passe_facil --todos --confirmar
python manage.py apagar_validacoes_teste --confirmar

# Criar novo conjunto de dados
python manage.py criar_usuarios_teste --quantidade 50
python manage.py gerar_eventos --quantidade 20
python manage.py criar_passe_facil_todos --confirmar
python manage.py gerar_validacoes_teste --quantidade 100 --dias-atras 90

# Apenas favoritos
python manage.py gerar_favoritos --quantidade 100

# Gerenciar Passe Fácil
python manage.py criar_passe_facil_todos --usuarios-ativos
python manage.py apagar_passe_facil --usuarios-inativos

# Gerenciar Validacões
python manage.py gerar_validacoes_teste --quantidade 500 --taxa-sucesso 0.95
python manage.py apagar_validacoes_teste --dias-recentes 7

# Gerenciar Notificações
python manage.py check_notifications --nao-lidas
python manage.py cleanup_notifications --dry-run
python manage.py criar_avisos_coop30 15
python manage.py criar_notificacoes_exemplo

# Verificar sistemas
python manage.py check_notifications --email admin@cop30.com
python manage.py cleanup_notifications

# Enviar notificações pendentes
python manage.py send_notifications
```

---





**Última atualização**: 26/11/2025  
**Versão**: 1.0.0  
**Status**: ✅ Funcional
