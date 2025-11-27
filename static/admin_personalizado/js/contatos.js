// ===== JAVASCRIPT PARA GERENCIAMENTO DE CONTATOS E REDES SOCIAIS =====

document.addEventListener('DOMContentLoaded', function() {
    // Elementos principais
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');
    
    // Dados cache
    let redesSociais = [];
    let contatos = [];
    let configuracoes = [];
    
    // ===== FUNCIONALIDADE DAS ABAS =====
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const targetTab = this.dataset.tab;
            
            // Remove classe active de todos os botões e painéis
            tabBtns.forEach(b => b.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));
            
            // Adiciona classe active ao botão clicado e painel correspondente
            this.classList.add('active');
            document.getElementById(targetTab).classList.add('active');
            
            // Carrega os dados da aba ativa
            carregarDadosAba(targetTab);
        });
    });
    
    // ===== CARREGAMENTO DE DADOS =====
    async function carregarDadosAba(aba) {
        switch(aba) {
            case 'redes-sociais':
                await carregarRedesSociais();
                break;
            case 'contatos':
                await carregarContatos();
                break;
            case 'configuracoes':
                await carregarConfiguracoes();
                break;
        }
    }
    
    // ===== REDES SOCIAIS =====
    async function carregarRedesSociais() {
        try {
            const response = await fetch('/meu-admin/api/redes-sociais/');
            if (response.ok) {
                redesSociais = await response.json();
                renderizarRedesSociais();
            } else {
                mostrarErro('Erro ao carregar redes sociais');
            }
        } catch (error) {
            console.error('Erro:', error);
            mostrarErro('Erro de conexão ao carregar redes sociais');
        }
    }
    
    function renderizarRedesSociais() {
        const container = document.getElementById('lista-redes-sociais');
        
        if (redesSociais.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fa-brands fa-hashtag"></i>
                    <h4>Nenhuma rede social cadastrada</h4>
                    <p>Clique em "Nova Rede Social" para adicionar a primeira</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = redesSociais
            .sort((a, b) => a.ordem - b.ordem)
            .map(rede => `
                <div class="item-card" data-id="${rede.id}">
                    <div class="item-header">
                        <div class="item-title">
                            <i class="${rede.icone}"></i>
                            <h4>${rede.nome}</h4>
                            <span class="status-badge ${rede.ativo ? 'ativo' : 'inativo'}">
                                ${rede.ativo ? 'Ativo' : 'Inativo'}
                            </span>
                        </div>
                        <div class="item-actions">
                            <button class="btn-edit" onclick="editarRedeSocial(${rede.id})">
                                <i class="fa-solid fa-edit"></i>
                                Editar
                            </button>
                            <button class="btn-danger" onclick="excluirRedeSocial(${rede.id})">
                                <i class="fa-solid fa-trash"></i>
                                Excluir
                            </button>
                        </div>
                    </div>
                    <div class="item-content">
                        <div class="item-field">
                            <strong>URL:</strong>
                            <span><a href="${rede.url}" target="_blank">${rede.url}</a></span>
                        </div>
                        <div class="item-field">
                            <strong>Ordem:</strong>
                            <span>${rede.ordem}</span>
                        </div>
                        <div class="item-field">
                            <strong>Ícone:</strong>
                            <span>${rede.icone}</span>
                        </div>
                    </div>
                </div>
            `).join('');
    }
    
    // ===== CONTATOS =====
    async function carregarContatos() {
        try {
            const response = await fetch('/meu-admin/api/contatos/');
            if (response.ok) {
                contatos = await response.json();
                renderizarContatos();
            } else {
                mostrarErro('Erro ao carregar contatos');
            }
        } catch (error) {
            console.error('Erro:', error);
            mostrarErro('Erro de conexão ao carregar contatos');
        }
    }
    
    function renderizarContatos() {
        const container = document.getElementById('lista-contatos');
        
        if (contatos.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fa-solid fa-address-book"></i>
                    <h4>Nenhum contato cadastrado</h4>
                    <p>Clique em "Novo Contato" para adicionar o primeiro</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = contatos
            .sort((a, b) => a.ordem - b.ordem)
            .map(contato => `
                <div class="item-card" data-id="${contato.id}">
                    <div class="item-header">
                        <div class="item-title">
                            <i class="${contato.icone}"></i>
                            <h4>${contato.tipo_contato_display || contato.tipo_contato}</h4>
                            <span class="status-badge ${contato.ativo ? 'ativo' : 'inativo'}">
                                ${contato.ativo ? 'Ativo' : 'Inativo'}
                            </span>
                        </div>
                        <div class="item-actions">
                            <button class="btn-edit" onclick="editarContato(${contato.id})">
                                <i class="fa-solid fa-edit"></i>
                                Editar
                            </button>
                            <button class="btn-danger" onclick="excluirContato(${contato.id})">
                                <i class="fa-solid fa-trash"></i>
                                Excluir
                            </button>
                        </div>
                    </div>
                    <div class="item-content">
                        <div class="item-field">
                            <strong>Valor:</strong>
                            <span>${contato.valor}</span>
                        </div>
                        <div class="item-field">
                            <strong>Ordem:</strong>
                            <span>${contato.ordem}</span>
                        </div>
                        <div class="item-field">
                            <strong>Ícone:</strong>
                            <span>${contato.icone}</span>
                        </div>
                    </div>
                </div>
            `).join('');
    }
    
    // ===== CONFIGURAÇÕES =====
    async function carregarConfiguracoes() {
        try {
            const response = await fetch('/meu-admin/api/configuracoes-site/');
            if (response.ok) {
                configuracoes = await response.json();
                renderizarConfiguracoes();
            } else {
                mostrarErro('Erro ao carregar configurações');
            }
        } catch (error) {
            console.error('Erro:', error);
            mostrarErro('Erro de conexão ao carregar configurações');
        }
    }
    
    function renderizarConfiguracoes() {
        const container = document.getElementById('lista-configuracoes');
        
        if (configuracoes.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fa-solid fa-cog"></i>
                    <h4>Nenhuma configuração cadastrada</h4>
                    <p>Clique em "Nova Configuração" para adicionar a primeira</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = configuracoes.map(config => `
            <div class="item-card" data-id="${config.id}">
                <div class="item-header">
                    <div class="item-title">
                        <i class="fa-solid fa-cog"></i>
                        <h4>${config.chave}</h4>
                    </div>
                    <div class="item-actions">
                        <button class="btn-edit" onclick="editarConfiguracao(${config.id})">
                            <i class="fa-solid fa-edit"></i>
                            Editar
                        </button>
                        <button class="btn-danger" onclick="excluirConfiguracao(${config.id})">
                            <i class="fa-solid fa-trash"></i>
                            Excluir
                        </button>
                    </div>
                </div>
                <div class="item-content">
                    <div class="item-field">
                        <strong>Valor:</strong>
                        <span>${config.valor}</span>
                    </div>
                    ${config.descricao ? `
                        <div class="item-field">
                            <strong>Descrição:</strong>
                            <span>${config.descricao}</span>
                        </div>
                    ` : ''}
                </div>
            </div>
        `).join('');
    }
    
    // ===== FORMULÁRIOS =====
    
    // Redes Sociais
    const formRedeSocial = document.getElementById('form-rede-social');
    const btnAddRede = document.getElementById('btn-add-rede');
    const btnCancelarRede = document.getElementById('btn-cancelar-rede');
    
    btnAddRede.addEventListener('click', () => {
        formRedeSocial.classList.remove('form-hidden');
        formRedeSocial.reset();
        document.getElementById('rede-id').value = '';
    });
    
    btnCancelarRede.addEventListener('click', () => {
        formRedeSocial.classList.add('form-hidden');
    });
    
    formRedeSocial.addEventListener('submit', async (e) => {
        e.preventDefault();
        await salvarRedeSocial();
    });
    
    // Controle do seletor de redes sociais
    const redeTipo = document.getElementById('rede-tipo');
    const redeNomeGroup = document.getElementById('rede-nome-group');
    const redeIconeGroup = document.getElementById('rede-icone-group');
    const redeNome = document.getElementById('rede-nome');
    const redeIcone = document.getElementById('rede-icone');
    const redeNomeHidden = document.getElementById('rede-nome-hidden');
    const redeIconeHidden = document.getElementById('rede-icone-hidden');
    
    // Dados pré-definidos das redes sociais
    const redesPredefinidas = {
        x: { nome: 'X', icone: 'fa-brands fa-x-twitter' },
        instagram: { nome: 'Instagram', icone: 'fa-brands fa-instagram' },
        linkedin: { nome: 'LinkedIn', icone: 'fa-brands fa-linkedin' },
        facebook: { nome: 'Facebook', icone: 'fa-brands fa-facebook' },
        youtube: { nome: 'YouTube', icone: 'fa-brands fa-youtube' }
    };
    
    redeTipo.addEventListener('change', (e) => {
        const tipo = e.target.value;
        
        if (tipo === 'outro') {
            // Mostrar campos para rede personalizada
            redeNomeGroup.style.display = 'block';
            redeIconeGroup.style.display = 'block';
            redeNome.required = true;
            redeIcone.required = true;
            redeNomeHidden.value = '';
            redeIconeHidden.value = '';
        } else if (tipo && redesPredefinidas[tipo]) {
            // Usar dados pré-definidos
            redeNomeGroup.style.display = 'none';
            redeIconeGroup.style.display = 'none';
            redeNome.required = false;
            redeIcone.required = false;
            redeNomeHidden.value = redesPredefinidas[tipo].nome;
            redeIconeHidden.value = redesPredefinidas[tipo].icone;
        } else {
            // Esconder todos os campos
            redeNomeGroup.style.display = 'none';
            redeIconeGroup.style.display = 'none';
            redeNome.required = false;
            redeIcone.required = false;
            redeNomeHidden.value = '';
            redeIconeHidden.value = '';
        }
        
        // Limpar campos personalizados quando mudar o tipo
        if (tipo !== 'outro') {
            redeNome.value = '';
            redeIcone.value = '';
        }
    });
    
    // Contatos
    const formContato = document.getElementById('form-contato');
    const btnAddContato = document.getElementById('btn-add-contato');
    const btnCancelarContato = document.getElementById('btn-cancelar-contato');
    
    btnAddContato.addEventListener('click', () => {
        formContato.classList.remove('form-hidden');
        formContato.reset();
        document.getElementById('contato-id').value = '';
    });
    
    btnCancelarContato.addEventListener('click', () => {
        formContato.classList.add('form-hidden');
    });
    
    formContato.addEventListener('submit', async (e) => {
        e.preventDefault();
        await salvarContato();
    });
    
    // Controle do seletor de contatos
    const contatoTipo = document.getElementById('contato-tipo');
    const contatoNomeGroup = document.getElementById('contato-nome-group');
    const contatoIconeGroup = document.getElementById('contato-icone-group');
    const contatoNome = document.getElementById('contato-nome');
    const contatoIcone = document.getElementById('contato-icone');
    const contatoNomeHidden = document.getElementById('contato-nome-hidden');
    const contatoIconeHidden = document.getElementById('contato-icone-hidden');
    
    // Dados pré-definidos dos tipos de contato
    const contatosPredefinidos = {
        email: { nome: 'E-mail', icone: 'fa-solid fa-envelope' },
        telefone: { nome: 'Telefone', icone: 'fa-solid fa-phone' },
        whatsapp: { nome: 'WhatsApp', icone: 'fa-brands fa-whatsapp' },
        endereco: { nome: 'Endereço', icone: 'fa-solid fa-location-dot' }
    };
    
    contatoTipo.addEventListener('change', (e) => {
        const tipo = e.target.value;
        
        if (tipo === 'outro') {
            // Mostrar campos para contato personalizado
            contatoNomeGroup.style.display = 'block';
            contatoIconeGroup.style.display = 'block';
            contatoNome.required = true;
            contatoIcone.required = true;
            contatoNomeHidden.value = '';
            contatoIconeHidden.value = '';
        } else if (tipo && contatosPredefinidos[tipo]) {
            // Usar dados pré-definidos
            contatoNomeGroup.style.display = 'none';
            contatoIconeGroup.style.display = 'none';
            contatoNome.required = false;
            contatoIcone.required = false;
            contatoNomeHidden.value = contatosPredefinidos[tipo].nome;
            contatoIconeHidden.value = contatosPredefinidos[tipo].icone;
        } else {
            // Esconder todos os campos
            contatoNomeGroup.style.display = 'none';
            contatoIconeGroup.style.display = 'none';
            contatoNome.required = false;
            contatoIcone.required = false;
            contatoNomeHidden.value = '';
            contatoIconeHidden.value = '';
        }
        
        // Limpar campos personalizados quando mudar o tipo
        if (tipo !== 'outro') {
            contatoNome.value = '';
            contatoIcone.value = '';
        }
    });
    
    // Configurações
    const formConfiguracao = document.getElementById('form-configuracao');
    const btnAddConfig = document.getElementById('btn-add-config');
    const btnCancelarConfig = document.getElementById('btn-cancelar-config');
    
    btnAddConfig.addEventListener('click', () => {
        formConfiguracao.classList.remove('form-hidden');
        formConfiguracao.reset();
        document.getElementById('config-id').value = '';
    });
    
    btnCancelarConfig.addEventListener('click', () => {
        formConfiguracao.classList.add('form-hidden');
    });
    
    formConfiguracao.addEventListener('submit', async (e) => {
        e.preventDefault();
        await salvarConfiguracao();
    });
    
    // ===== SALVAR DADOS =====
    async function salvarRedeSocial() {
        const formData = new FormData(formRedeSocial);
        const id = formData.get('id');
        const url = id ? '/meu-admin/api/redes-sociais/' + id + '/' : '/meu-admin/api/redes-sociais/';
        const method = id ? 'PUT' : 'POST';
        
        // Determinar nome e ícone com base no tipo selecionado
        const tipo = formData.get('tipo');
        let nome, icone;
        
        if (tipo === 'outro') {
            nome = formData.get('nome');
            icone = formData.get('icone');
        } else if (redesPredefinidas[tipo]) {
            nome = redesPredefinidas[tipo].nome;
            icone = redesPredefinidas[tipo].icone;
        } else {
            mostrarErro('Por favor, selecione um tipo de rede social');
            return;
        }
        
        try {
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                },
                body: JSON.stringify({
                    nome: nome,
                    icone: icone,
                    url: formData.get('url'),
                    ordem: formData.get('ordem'),
                    ativo: formData.get('ativo') === 'true'
                })
            });
            
            if (response.ok) {
                mostrarSucesso('Rede social salva com sucesso!');
                formRedeSocial.classList.add('form-hidden');
                await carregarRedesSociais();
            } else {
                const error = await response.json();
                mostrarErro('Erro ao salvar rede social: ' + (error.message || 'Tente novamente'));
            }
        } catch (error) {
            console.error('Erro:', error);
            mostrarErro('Erro de conexão ao salvar rede social');
        }
    }
    
    async function salvarContato() {
        const formData = new FormData(formContato);
        const id = formData.get('id');
        const url = id ? '/meu-admin/api/contatos/' + id + '/' : '/meu-admin/api/contatos/';
        const method = id ? 'PUT' : 'POST';
        
        // Determinar nome e ícone com base no tipo selecionado
        const tipo = formData.get('tipo_contato');
        let nome, icone;
        
        if (tipo === 'outro') {
            nome = formData.get('nome');
            icone = formData.get('icone');
        } else if (contatosPredefinidos[tipo]) {
            nome = contatosPredefinidos[tipo].nome;
            icone = contatosPredefinidos[tipo].icone;
        } else {
            mostrarErro('Por favor, selecione um tipo de contato');
            return;
        }
        
        try {
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                },
                body: JSON.stringify({
                    tipo_contato: nome,
                    icone: icone,
                    valor: formData.get('valor'),
                    ordem: formData.get('ordem'),
                    ativo: formData.get('ativo') === 'true'
                })
            });
            
            if (response.ok) {
                mostrarSucesso('Contato salvo com sucesso!');
                formContato.classList.add('form-hidden');
                await carregarContatos();
            } else {
                const error = await response.json();
                mostrarErro('Erro ao salvar contato: ' + (error.message || 'Tente novamente'));
            }
        } catch (error) {
            console.error('Erro:', error);
            mostrarErro('Erro de conexão ao salvar contato');
        }
    }
    
    async function salvarConfiguracao() {
        const formData = new FormData(formConfiguracao);
        const id = formData.get('id');
        const url = id ? '/meu-admin/api/configuracoes-site/' + id + '/' : '/meu-admin/api/configuracoes-site/';
        const method = id ? 'PUT' : 'POST';
        
        try {
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                },
                body: JSON.stringify({
                    chave: formData.get('chave'),
                    valor: formData.get('valor'),
                    descricao: formData.get('descricao')
                })
            });
            
            if (response.ok) {
                mostrarSucesso('Configuração salva com sucesso!');
                formConfiguracao.classList.add('form-hidden');
                await carregarConfiguracoes();
            } else {
                const error = await response.json();
                mostrarErro('Erro ao salvar configuração: ' + (error.message || 'Tente novamente'));
            }
        } catch (error) {
            console.error('Erro:', error);
            mostrarErro('Erro de conexão ao salvar configuração');
        }
    }
    
    // ===== EDITAR =====
    window.editarRedeSocial = async function(id) {
        const rede = redesSociais.find(r => r.id === id);
        if (rede) {
            document.getElementById('rede-id').value = rede.id;
            document.getElementById('rede-url').value = rede.url;
            document.getElementById('rede-ordem').value = rede.ordem;
            document.getElementById('rede-ativo').value = rede.ativo.toString();
            
            // Verificar se é uma rede pré-definida
            let tipoSelecionado = 'outro';
            for (const [tipo, dados] of Object.entries(redesPredefinidas)) {
                if (dados.nome === rede.nome && dados.icone === rede.icone) {
                    tipoSelecionado = tipo;
                    break;
                }
            }
            
            document.getElementById('rede-tipo').value = tipoSelecionado;
            
            // Disparar evento change para mostrar/esconder campos corretos
            const event = new Event('change', { bubbles: true });
            document.getElementById('rede-tipo').dispatchEvent(event);
            
            // Se for "outro", preencher os campos personalizados
            if (tipoSelecionado === 'outro') {
                document.getElementById('rede-nome').value = rede.nome;
                document.getElementById('rede-icone').value = rede.icone;
            }
            
            formRedeSocial.classList.remove('form-hidden');
        }
    };
    
    window.editarContato = async function(id) {
        const contato = contatos.find(c => c.id === id);
        if (contato) {
            document.getElementById('contato-id').value = contato.id;
            document.getElementById('contato-valor').value = contato.valor;
            document.getElementById('contato-ordem').value = contato.ordem;
            document.getElementById('contato-ativo').value = contato.ativo.toString();
            
            // Verificar se é um contato pré-definido
            let tipoSelecionado = 'outro';
            for (const [tipo, dados] of Object.entries(contatosPredefinidos)) {
                if (dados.nome === contato.tipo_contato && dados.icone === contato.icone) {
                    tipoSelecionado = tipo;
                    break;
                }
            }
            
            document.getElementById('contato-tipo').value = tipoSelecionado;
            
            // Disparar evento change para mostrar/esconder campos corretos
            const event = new Event('change', { bubbles: true });
            document.getElementById('contato-tipo').dispatchEvent(event);
            
            // Se for "outro", preencher os campos personalizados
            if (tipoSelecionado === 'outro') {
                document.getElementById('contato-nome').value = contato.tipo_contato;
                document.getElementById('contato-icone').value = contato.icone;
            }
            
            formContato.classList.remove('form-hidden');
        }
    };
    
    window.editarConfiguracao = async function(id) {
        const config = configuracoes.find(c => c.id === id);
        if (config) {
            document.getElementById('config-id').value = config.id;
            document.getElementById('config-chave').value = config.chave;
            document.getElementById('config-valor').value = config.valor;
            document.getElementById('config-descricao').value = config.descricao || '';
            formConfiguracao.classList.remove('form-hidden');
        }
    };
    
    // ===== EXCLUIR =====
    window.excluirRedeSocial = async function(id) {
        if (confirm('Tem certeza que deseja excluir esta rede social?')) {
            try {
                const response = await fetch('/meu-admin/api/redes-sociais/' + id + '/', {
                    method: 'DELETE',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                });
                
                if (response.ok) {
                    mostrarSucesso('Rede social excluída com sucesso!');
                    await carregarRedesSociais();
                } else {
                    mostrarErro('Erro ao excluir rede social');
                }
            } catch (error) {
                console.error('Erro:', error);
                mostrarErro('Erro de conexão ao excluir rede social');
            }
        }
    };
    
    window.excluirContato = async function(id) {
        if (confirm('Tem certeza que deseja excluir este contato?')) {
            try {
                const response = await fetch('/meu-admin/api/contatos/' + id + '/', {
                    method: 'DELETE',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                });
                
                if (response.ok) {
                    mostrarSucesso('Contato excluído com sucesso!');
                    await carregarContatos();
                } else {
                    mostrarErro('Erro ao excluir contato');
                }
            } catch (error) {
                console.error('Erro:', error);
                mostrarErro('Erro de conexão ao excluir contato');
            }
        }
    };
    
    window.excluirConfiguracao = async function(id) {
        if (confirm('Tem certeza que deseja excluir esta configuração?')) {
            try {
                const response = await fetch('/meu-admin/api/configuracoes-site/' + id + '/', {
                    method: 'DELETE',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    }
                });
                
                if (response.ok) {
                    mostrarSucesso('Configuração excluída com sucesso!');
                    await carregarConfiguracoes();
                } else {
                    mostrarErro('Erro ao excluir configuração');
                }
            } catch (error) {
                console.error('Erro:', error);
                mostrarErro('Erro de conexão ao excluir configuração');
            }
        }
    };
    
    // ===== NOTIFICAÇÕES =====
    function mostrarSucesso(mensagem) {
        // Implementar sistema de notificações (pode usar o mesmo do baseadmin)
        alert('Sucesso: ' + mensagem);
    }
    
    function mostrarErro(mensagem) {
        // Implementar sistema de notificações (pode usar o mesmo do baseadmin)
        alert('Erro: ' + mensagem);
    }
    
    // ===== INICIALIZAÇÃO =====
    // Carrega a primeira aba ativa
    const activeTab = document.querySelector('.tab-btn.active');
    if (activeTab) {
        carregarDadosAba(activeTab.dataset.tab);
    }
});
