/**
 * Gerenciamento de Eventos - Admin
 * Integração com a API de eventos
 */

document.addEventListener('DOMContentLoaded', function() {
    const formEvento = document.getElementById('form-evento');
    const listaEventos = document.getElementById('lista-eventos');
    const formTitle = document.getElementById('form-title');
    const eventoIdInput = document.getElementById('evento-id');
    const btnCancelar = document.getElementById('btn-cancelar');
    const filtroData = document.getElementById('filtro-data');
    
    // URLs da API
    const API_URLS = {
        listar: '/admin/api/eventos/',
        criar: '/admin/eventos/novo/',
        editar: (id) => `/admin/eventos/${id}/editar/`,
        excluir: (id) => `/admin/eventos/${id}/excluir/`
    };
    
    // Estado da aplicação
    let eventos = [];
    let modoEdicao = false;
    
    // Inicialização
    function init() {
        carregarEventos();
        configurarEventListeners();
    }
    
    // Configura os event listeners
    function configurarEventListeners() {
        // Formulário de evento
        if (formEvento) {
            formEvento.addEventListener('submit', salvarEvento);
        }
        
        // Botão cancelar
        if (btnCancelar) {
            btnCancelar.addEventListener('click', limparFormulario);
        }
        
        // Filtro de data
        if (filtroData) {
            filtroData.addEventListener('change', () => carregarEventos(filtroData.value));
        }
        
        // Delegação de eventos para os botões de editar/excluir
        if (listaEventos) {
            listaEventos.addEventListener('click', (e) => {
                const target = e.target.closest('[data-action]');
                if (!target) return;
                
                const acao = target.getAttribute('data-action');
                const card = target.closest('.event-card');
                const eventoId = card ? parseInt(card.dataset.id) : null;
                
                if (acao === 'editar' && eventoId) {
                    carregarEventoParaEdicao(eventoId);
                } else if (acao === 'excluir' && eventoId) {
                    confirmarExclusao(eventoId);
                }
            });
        }
    }
    
    // Carrega os eventos da API
    async function carregarEventos(filtro = 'todos') {
        try {
            mostrarLoading(true);
            const response = await fetch(`${API_URLS.listar}?filtro=${filtro}`);
            const data = await response.json();
            
            if (data.success) {
                eventos = data.eventos;
                renderizarEventos(eventos);
            } else {
                throw new Error(data.message || 'Erro ao carregar eventos');
            }
        } catch (error) {
            console.error('Erro:', error);
            mostrarMensagem('error', 'Erro ao carregar eventos. Tente novamente.');
        } finally {
            mostrarLoading(false);
        }
    }
    
    // Renderiza a lista de eventos
    function renderizarEventos(eventos) {
        if (!listaEventos) return;
        
        if (eventos.length === 0) {
            listaEventos.innerHTML = `
                <div class="alert alert-info">
                    Nenhum evento encontrado.
                </div>
            `;
            return;
        }
        
        listaEventos.innerHTML = eventos.map(evento => `
            <div class="event-card card mb-3" data-id="${evento.id}">
                <div class="card-body">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <h5 class="card-title mb-1">
                                ${evento.titulo}
                                ${evento.importante ? '<span class="badge bg-warning text-dark ms-2">Importante</span>' : ''}
                            </h5>
                            <p class="text-muted mb-2">
                                <i class="far fa-calendar-alt me-1"></i> 
                                ${formatarData(evento.data_inicio)}
                                <span class="mx-2">•</span>
                                <i class="far fa-clock me-1"></i>
                                ${formatarHora(evento.data_inicio)} - ${formatarHora(evento.data_fim)}
                            </p>
                            <p class="card-text">${evento.descricao || 'Sem descrição'}</p>
                            <p class="mb-0">
                                <i class="fas fa-map-marker-alt me-1"></i>
                                ${evento.local || 'Local não informado'}
                            </p>
                            ${evento.tema ? `
                                <p class="mb-0">
                                    <i class="fas fa-tag me-1"></i>
                                    ${evento.tema}
                                </p>
                            ` : ''}
                        </div>
                        <div class="btn-group">
                            <button class="btn btn-sm btn-outline-primary" data-action="editar">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-sm btn-outline-danger" data-action="excluir">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }
    
    // Carrega um evento para edição
    async function carregarEventoParaEdicao(eventoId) {
        try {
            const response = await fetch(`/admin/api/eventos/${eventoId}/`);
            const data = await response.json();
            
            if (data.success) {
                const evento = data.evento;
                
                // Preenche o formulário
                formTitle.textContent = 'Editar Evento';
                formEvento.querySelector('button[type="submit"]').textContent = 'Atualizar Evento';
                
                // Preenche os campos
                eventoIdInput.value = evento.id;
                document.getElementById('evento-titulo').value = evento.titulo;
                document.getElementById('evento-descricao').value = evento.descricao;
                document.getElementById('evento-local').value = evento.local;
                document.getElementById('evento-data').value = evento.data;
                document.getElementById('evento-inicio').value = evento.inicio;
                document.getElementById('evento-fim').value = evento.fim;
                document.getElementById('evento-tema').value = evento.tema;
                document.getElementById('evento-importante').checked = evento.importante;
                
                // Rola até o formulário
                formEvento.scrollIntoView({ behavior: 'smooth' });
                
                modoEdicao = true;
            } else {
                throw new Error(data.message || 'Erro ao carregar evento');
            }
        } catch (error) {
            console.error('Erro:', error);
            mostrarMensagem('error', 'Erro ao carregar evento para edição.');
        }
    }
    
    // Salva um evento (cria ou atualiza)
    async function salvarEvento(e) {
        e.preventDefault();
        
        const formData = new FormData(formEvento);
        const eventoId = eventoIdInput.value;
        const url = modoEdicao ? API_URLS.editar(eventoId) : API_URLS.criar;
        const method = modoEdicao ? 'POST' : 'POST';
        
        const dados = {
            titulo: formData.get('titulo'),
            descricao: formData.get('descricao'),
            local: formData.get('local'),
            data: formData.get('data'),
            inicio: formData.get('inicio'),
            fim: formData.get('fim'),
            tema: formData.get('tema') || ''
        };
        
        try {
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(dados)
            });
            
            const result = await response.json();
            
            if (result.success) {
                mostrarMensagem('success', 
                    modoEdicao ? 'Evento atualizado com sucesso!' : 'Evento criado com sucesso!');
                limparFormulario();
                carregarEventos(filtroData ? filtroData.value : 'todos');
            } else {
                throw new Error(result.message || 'Erro ao salvar evento');
            }
        } catch (error) {
            console.error('Erro:', error);
            mostrarMensagem('error', 'Erro ao salvar evento. Tente novamente.');
        }
    }
    
    // Confirma a exclusão de um evento
    function confirmarExclusao(eventoId) {
        if (confirm('Tem certeza que deseja excluir este evento?')) {
            excluirEvento(eventoId);
        }
    }
    
    // Exclui um evento
    async function excluirEvento(eventoId) {
        try {
            const response = await fetch(API_URLS.excluir(eventoId), {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                mostrarMensagem('success', 'Evento excluído com sucesso!');
                carregarEventos(filtroData ? filtroData.value : 'todos');
            } else {
                throw new Error(result.message || 'Erro ao excluir evento');
            }
        } catch (error) {
            console.error('Erro:', error);
            mostrarMensagem('error', 'Erro ao excluir evento. Tente novamente.');
        }
    }
    
    // Limpa o formulário
    function limparFormulario() {
        formEvento.reset();
        eventoIdInput.value = '';
        formTitle.textContent = 'Criar Novo Evento';
        formEvento.querySelector('button[type="submit"]').textContent = 'Salvar Evento';
        modoEdicao = false;
    }
    
    // Mostra/esconde o indicador de carregamento
    function mostrarLoading(mostrar) {
        const loadingElement = document.getElementById('loading-indicator');
        if (loadingElement) {
            loadingElement.style.display = mostrar ? 'block' : 'none';
        }
    }
    
    // Mostra uma mensagem para o usuário
    function mostrarMensagem(tipo, mensagem) {
        // Implemente a exibição de mensagens conforme necessário
        console.log(`[${tipo.toUpperCase()}] ${mensagem}`);
        // Exemplo com SweetAlert2 ou similar
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                icon: tipo,
                text: mensagem,
                toast: true,
                position: 'top-end',
                showConfirmButton: false,
                timer: 3000
            });
        } else {
            alert(mensagem);
        }
    }
    
    // Funções auxiliares
    function formatarData(dataString) {
        if (!dataString) return '';
        const options = { day: '2-digit', month: '2-digit', year: 'numeric' };
        return new Date(dataString).toLocaleDateString('pt-BR', options);
    }
    
    function formatarHora(dataString) {
        if (!dataString) return '';
        const date = new Date(dataString);
        return date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
    }
    
    function getCookie(name) {
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
    }
    
    // Inicializa a aplicação
    init();
});

// Adiciona um polyfill para o closest() caso necessário
if (!Element.prototype.matches) {
    Element.prototype.matches = 
        Element.prototype.msMatchesSelector || 
        Element.prototype.webkitMatchesSelector;
}

if (!Element.prototype.closest) {
    Element.prototype.closest = function(s) {
        let el = this;
        do {
            if (el.matches(s)) return el;
            el = el.parentElement || el.parentNode;
        } while (el !== null && el.nodeType === 1);
        return null;
    };
}
