// Adiciona suporte a URL base dinâmica
const BASE_URL = window.location.pathname.includes('meu-admin') ? '/meu-admin' : '';

document.addEventListener('DOMContentLoaded', () => {
    const formAviso = document.getElementById('form-aviso');
    const listaAvisosAtivos = document.getElementById('lista-avisos-ativos');
    const listaHistorico = document.getElementById('lista-historico');
    const selectImportancia = document.getElementById('aviso-importancia');

    // --- FUNÇÕES DE RENDERIZAÇÃO ---
    const renderizarAvisos = (avisosAtivos, avisosHistorico) => {
        try {
            // Renderizar avisos ativos
            if (listaAvisosAtivos) {
                listaAvisosAtivos.innerHTML = '';
                if (!avisosAtivos || avisosAtivos.length === 0) {
                    listaAvisosAtivos.innerHTML = '<p class="empty-state">Nenhum aviso ativo no momento.</p>';
                } else {
                    avisosAtivos.forEach(aviso => {
                        const card = criarCardAviso(aviso);
                        if (card) listaAvisosAtivos.appendChild(card);
                    });
                }
            }

            // Renderizar histórico
            if (listaHistorico) {
                listaHistorico.innerHTML = '';
                if (!avisosHistorico || avisosHistorico.length === 0) {
                    listaHistorico.innerHTML = '<p class="empty-state">Nenhum aviso no histórico.</p>';
                } else {
                    avisosHistorico.forEach(aviso => {
                        const item = criarItemHistorico(aviso);
                        if (item) listaHistorico.appendChild(item);
                    });
                }
            }
        } catch (error) {
            console.error('Erro ao renderizar avisos:', error);
        }
    };

    // --- FUNÇÕES DE CRIAÇÃO DE ELEMENTOS ---
    const criarCardAviso = (aviso) => {
        if (!aviso) return null;
        
        try {
            const card = document.createElement('div');
            card.className = `notice-card ${aviso.nivel || 'info'}`;
            card.dataset.id = aviso.id;
            
            const dataExpiracao = aviso.data_expiracao ? 
                new Date(aviso.data_expiracao).toLocaleString('pt-BR') : 
                'Não expira';
            
            card.innerHTML = `
                <div class="notice-content">
                    <h4>${aviso.titulo || 'Sem título'}</h4>
                    <p>${aviso.mensagem || 'Sem mensagem'}</p>
                    <span class="notice-info">Expira em: ${dataExpiracao}</span>
                </div>
                <div class="notice-actions">
                    <button class="pin-btn ${aviso.fixo_no_topo ? 'pinned' : ''}" 
                            title="Fixar no topo" 
                            data-id="${aviso.id}">
                        <i class="fa-solid fa-thumbtack"></i>
                    </button>
                    <button class="delete-btn" title="Excluir" data-id="${aviso.id}">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </div>
            `;
            return card;
        } catch (error) {
            console.error('Erro ao criar card de aviso:', error);
            return null;
        }
    };

    const criarItemHistorico = (aviso) => {
        if (!aviso) return null;
        
        try {
            const item = document.createElement('div');
            item.className = 'history-item';
            item.innerHTML = `
                <span class="history-title">${aviso.titulo || 'Sem título'}</span>
                <span class="history-date">
                    ${new Date(aviso.data_criacao).toLocaleString('pt-BR')}
                </span>
            `;
            return item;
        } catch (error) {
            console.error('Erro ao criar item de histórico:', error);
            return null;
        }
    };

    // --- FUNÇÃO PARA OBTER CSRF TOKEN ---
    const getCookie = (name) => {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    };

    const csrftoken = getCookie('csrftoken');

    // --- FUNÇÃO PARA CARREGAR AVISOS VIA API ---
    const carregarAvisos = async () => {
        try {
            console.log('Carregando avisos...');
            const response = await fetch(`${BASE_URL}/api/avisos/`, {
                headers: {
                    'Accept': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            if (!response.ok) {
                throw new Error(`Erro HTTP: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('Dados recebidos:', data);
            
            if (data && data.avisos_ativos !== undefined && data.avisos_historico !== undefined) {
                renderizarAvisos(data.avisos_ativos, data.avisos_historico);
            } else {
                console.error('Formato de dados inesperado:', data);
                alert('Erro: Formato de dados inesperado ao carregar avisos.');
            }
        } catch (error) {
            console.error('Erro ao carregar avisos:', error);
            alert('Não foi possível carregar os avisos. Por favor, tente novamente mais tarde.');
        }
    };

    // --- EVENT LISTENER DO FORMULÁRIO ---
    if (formAviso) {
        formAviso.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            try {
                const formData = new FormData(formAviso);
                const data = {
                    titulo: formData.get('titulo'),
                    mensagem: formData.get('mensagem'),
                    nivel: formData.get('nivel'),
                    data_expiracao: formData.get('data_expiracao') || null,
                    fixo_no_topo: formData.get('fixo_no_topo') === 'on'
                };

                const response = await fetch(`${BASE_URL}/api/avisos/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrftoken,
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: JSON.stringify(data)
                });

                if (!response.ok) {
                    throw new Error(`Erro HTTP: ${response.status}`);
                }

                const result = await response.json();
                if (result.success) {
                    formAviso.reset();
                    await carregarAvisos();
                    alert('Aviso salvo com sucesso!');
                } else {
                    throw new Error(result.message || 'Erro ao salvar o aviso');
                }
            } catch (error) {
                console.error('Erro ao salvar aviso:', error);
                alert(`Erro ao salvar aviso: ${error.message}`);
            }
        });
    }

// ... código anterior ...

// --- EVENT LISTENER PARA AÇÕES NOS AVISOS ---
if (listaAvisosAtivos) {
    listaAvisosAtivos.addEventListener('click', async (e) => {
        const target = e.target.closest('button');
        if (!target) return;
        
        try {
            const avisoId = target.dataset.id;
            if (!avisoId) return;

            if (target.classList.contains('delete-btn')) {
                if (!confirm('Tem certeza que deseja excluir este aviso?')) {
                    return;
                }

                const response = await fetch(`${BASE_URL}/avisos/${avisoId}/excluir/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrftoken,
                        'X-Requested-With': 'XMLHttpRequest',
                        'Content-Type': 'application/json'
                    }
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    throw new Error(errorData.message || `Erro HTTP: ${response.status}`);
                }

                const result = await response.json();
                if (result.success) {
                    await carregarAvisos();
                    alert('Aviso excluído com sucesso!');
                } else {
                    throw new Error(result.message || 'Erro ao excluir aviso');
                }
            } 
            
            else if (target.classList.contains('pin-btn')) {
                const response = await fetch(`${BASE_URL}/avisos/${avisoId}/fixar/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrftoken,
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                });

                if (!response.ok) {
                    throw new Error('Erro ao fixar/desfixar aviso');
                }

                const result = await response.json();
                if (result.success) {
                    await carregarAvisos();
                } else {
                    throw new Error(result.message || 'Erro ao fixar/desfixar aviso');
                }
            }
        } catch (error) {
            console.error('Erro ao processar ação:', error);
            alert(`Erro: ${error.message}`);
        }
    });
}

    // --- INICIALIZAÇÃO ---
    if (window.location.pathname.includes('avisos')) {
        carregarAvisos();
        
        // Atualiza a cada 30 segundos
        setInterval(carregarAvisos, 30000);
    }
});