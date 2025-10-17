document.addEventListener('DOMContentLoaded', () => {
    // Elementos do DOM
    const formEvento = document.querySelector('#form-evento');
    const listaEventos = document.getElementById('lista-eventos');
    const eventoIdInput = document.getElementById('evento-id');
    const searchInput = document.getElementById('search-input');
    const confirmModal = document.getElementById('confirm-modal');
    
    // Verifica se os elementos necessários existem
    if (!formEvento || !listaEventos) {
        console.error('Elementos necessários não encontrados');
        return;
    }
    
    // URLs da API
    const API_BASE = '/meu-admin';
    const API_URL = `${API_BASE}/eventos/`;
    const API_EVENTOS = `${API_BASE}/api/eventos/`;
    
    // Função auxiliar para construir URLs da API
    const getEventUrl = (eventoId = '') => {
        return eventoId ? `${API_URL}${eventoId}/` : `${API_URL}novo/`;
    };
    
    // Estado da aplicação
    let eventos = [];
    let editMode = false;
    
    // Obtém o token CSRF
    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]')?.value;
    if (!csrfToken) {
        console.error('Token CSRF não encontrado');
        showAlert('Erro de segurança. Por favor, recarregue a página.', 'error');
        return;
    }
    
    // Inicialização
    initEventListeners();
    carregarEventos();
    atualizarContadores();
    
    /**
     * Inicializa os event listeners
     */
    function initEventListeners() {
        // Formulário de evento
        formEvento.addEventListener('submit', handleFormSubmit);
        
        // Botão de limpar formulário
        const btnLimpar = document.getElementById('btn-limpar');
        if (btnLimpar) {
            btnLimpar.addEventListener('click', resetarFormulario);
        }
        
        // Botão de atualizar
        const btnAtualizar = document.getElementById('btn-atualizar');
        if (btnAtualizar) {
            btnAtualizar.addEventListener('click', async () => {
                btnAtualizar.classList.add('rotating');
                await Promise.all([carregarEventos(), atualizarContadores()]);
                setTimeout(() => btnAtualizar.classList.remove('rotating'), 500);
            });
        }
        
        // Barra de pesquisa
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                pesquisarEventos(e.target.value.trim());
            });
        }
        
        // Filtro de status
        const filterStatus = document.getElementById('filter-status');
        if (filterStatus) {
            filterStatus.addEventListener('change', (e) => {
                filtrarEventosPorStatus(e.target.value);
            });
        }
        
        // Modal de confirmação
        if (confirmModal) {
            // Fechar modal ao clicar no X ou no botão de cancelar
            document.querySelectorAll('.close-modal, #btn-cancelar-exclusao').forEach(btn => {
                btn.addEventListener('click', () => toggleModal(false));
            });
            
            // Fechar modal ao clicar fora
            confirmModal.addEventListener('click', (e) => {
                if (e.target === confirmModal) toggleModal(false);
            });
            
            // Confirmar exclusão
            const btnConfirmar = document.getElementById('btn-confirmar-exclusao');
            if (btnConfirmar) {
                btnConfirmar.addEventListener('click', handleConfirmarExclusao);
            }
        }
    }
    
    /**
     * Manipula o envio do formulário
     */
    async function handleFormSubmit(e) {
        e.preventDefault();
        
        const formData = {
            titulo: getFormValue('evento-titulo'),
            descricao: getFormValue('evento-descricao'),
            local: getFormValue('evento-local'),
            start_time: `${getFormValue('evento-data')}T${getFormValue('evento-inicio')}`,
            end_time: `${getFormValue('evento-data')}T${getFormValue('evento-fim')}`,
            tags: getFormValue('evento-tags'),
            importante: document.getElementById('evento-importante')?.checked || false
        };
        
        if (!validarFormulario(formData)) {
            return;
        }
        
        const id = eventoIdInput?.value;
        const url = getEventUrl(id);
        const method = id ? 'PUT' : 'POST';
        
        try {
            const response = await fetch(url, {
                method,
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify(formData)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Erro ao salvar evento');
            }
            
            const successMessage = id ? 'Evento atualizado com sucesso!' : 'Evento criado com sucesso!';
            showAlert(successMessage, 'success');
            
            await Promise.all([carregarEventos(), atualizarContadores()]);
            resetarFormulario();
            
        } catch (error) {
            console.error('Erro ao salvar evento:', error);
            showAlert(error.message || 'Erro ao processar a requisição', 'error');
        }
    }
    
    /**
     * Manipula a confirmação de exclusão
     */
    async function handleConfirmarExclusao() {
        const modal = document.getElementById('confirm-modal');
        if (!modal) return;
        
        const eventoId = modal.dataset.eventoId;
        if (!eventoId) {
            console.error('ID do evento não encontrado');
            return;
        }
        
        try {
            const response = await fetch(getEventUrl(eventoId), {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || 'Erro ao excluir evento');
            }
            
            showAlert('Evento excluído com sucesso!', 'success');
            await carregarEventos();
            atualizarContadores();
            
        } catch (error) {
            console.error('Erro ao excluir evento:', error);
            showAlert(error.message || 'Erro ao excluir evento', 'error');
        } finally {
            toggleModal(false);
        }
    }

    /**
     * Exibe uma mensagem de feedback para o usuário
     * @param {string} message - A mensagem a ser exibida
     * @param {string} type - O tipo de alerta (success, error, warning, info)
     */
    function showAlert(message, type = 'success') {
        // Remove alertas existentes
        const existingAlert = document.querySelector('.alert');
        if (existingAlert) {
            existingAlert.remove();
        }
        
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type}`;
        alertDiv.innerHTML = `
            <div class="alert-content">
                <i class="fas ${getAlertIcon(type)}"></i>
                <span>${message}</span>
            </div>
            <button class="alert-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        // Insere o alerta após o cabeçalho
        const header = document.querySelector('.main-header');
        if (header) {
            header.insertAdjacentElement('afterend', alertDiv);
            
            // Remove o alerta após 5 segundos
            setTimeout(() => {
                alertDiv.classList.add('fade-out');
                setTimeout(() => alertDiv.remove(), 300);
            }, 5000);
        }
    }
    
    /**
     * Retorna o ícone correspondente ao tipo de alerta
     */
    function getAlertIcon(type) {
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };
        return icons[type] || 'fa-info-circle';
    }

    /**
     * Formata uma data para o formato brasileiro
     */
    function formatDate(dateString) {
        if (!dateString) return '';
        const date = new Date(dateString);
        return date.toLocaleDateString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    /**
     * Formata apenas a hora
     */
    function formatTime(timeString) {
        if (!timeString) return '';
        const [hours, minutes] = timeString.split(':');
        return `${hours.padStart(2, '0')}:${minutes || '00'}`;
    }

    /**
     * Carrega os eventos da API
     */
    async function carregarEventos() {
        try {
            const response = await fetch(API_EVENTOS);
            if (!response.ok) {
                throw new Error('Erro ao carregar eventos');
            }
            
            eventos = await response.json();
            renderizarEventos();
            return eventos;
        } catch (error) {
            console.error('Erro ao carregar eventos:', error);
            showAlert('Não foi possível carregar os eventos. Tente novamente mais tarde.', 'error');
            return [];
        }
    }
    
    /**
     * Atualiza os contadores de eventos
     */
    async function atualizarContadores() {
        try {
            const hoje = new Date().toISOString().split('T')[0];
            const total = eventos.length;
            const hojeCount = eventos.filter(e => e.start_time?.startsWith(hoje)).length;
            const destaqueCount = eventos.filter(e => e.importante).length;
            
            // Atualiza os elementos da interface
            document.getElementById('total-eventos').textContent = total;
            document.getElementById('eventos-hoje').textContent = hojeCount;
            document.getElementById('eventos-destaque').textContent = destaqueCount;
            
            return { total, hoje: hojeCount, destaque: destaqueCount };
        } catch (error) {
            console.error('Erro ao atualizar contadores:', error);
            return { total: 0, hoje: 0, destaque: 0 };
        }
    }

    // Renderizar lista de eventos
    const renderizarEventos = (eventosFiltrados = null) => {
        const eventosParaRenderizar = eventosFiltrados || eventos;
        listaEventos.innerHTML = '';
        
        if (eventosParaRenderizar.length === 0) {
            listaEventos.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-calendar-alt fa-3x mb-3"></i>
                    <p>Nenhum evento encontrado.</p>
                </div>`;
            return;
        }
        
        eventosParaRenderizar.forEach(evento => {
            listaEventos.appendChild(criarCardEvento(evento));
        });
    };

    // Criar card de evento
    const criarCardEvento = (evento) => {
        const card = document.createElement('div');
        card.className = `event-card`;
        card.dataset.id = evento.id;
        
        const dataEvento = formatDate(evento.start_time);
        const horaInicio = formatTime(evento.start_time?.split('T')[1]);
        const horaFim = formatTime(evento.end_time?.split('T')[1]);
        
        card.innerHTML = `
            <div class="event-details">
                <h4>${evento.titulo}</h4>
                <p>${evento.descricao || 'Sem descrição'}</p>
                <div class="event-meta">
                    <span><i class="fa-solid fa-calendar-day"></i> ${dataEvento}</span>
                    <span><i class="fa-solid fa-clock"></i> ${horaInicio} - ${horaFim}</span>
                    <span><i class="fa-solid fa-location-dot"></i> ${evento.local || 'Local não informado'}</span>
                </div>
            </div>
            <div class="event-actions">
                <button type="button" class="edit-btn" title="Editar"><i class="fa-solid fa-pencil"></i></button>
                <button type="button" class="delete-btn" title="Remover"><i class="fa-solid fa-trash"></i></button>
            </div>
        `;
        return card;
    };

    // Resetar formulário
    const resetarFormulario = () => {
        if (!formEvento) {
            console.error('Formulário não encontrado para reset');
            return;
        }
        
        try {
            // Reseta o formulário
            formEvento.reset();
            
            // Limpa o ID do evento
            if (eventoIdInput) {
                eventoIdInput.value = '';
            }
            
            // Define a data padrão para hoje
            const hoje = new Date().toISOString().split('T')[0];
            const dataInput = document.getElementById('evento-data');
            if (dataInput) {
                const today = new Date();
                const year = today.getFullYear();
                const month = String(today.getMonth() + 1).padStart(2, '0');
                const day = String(today.getDate()).padStart(2, '0');
                dataInput.value = `${year}-${month}-${day}`;
            }
            
            // Define horário padrão (08:00 - 09:00)
            const horaInicio = document.getElementById('evento-inicio');
            const horaFim = document.getElementById('evento-fim');
            
            if (horaInicio) horaInicio.value = '08:00';
            if (horaFim) horaFim.value = '09:00';
            
            // Reseta o tema para o padrão
            const temaSelect = document.getElementById('evento-tema');
            if (temaSelect) temaSelect.value = 'sustentabilidade';
            
            // Desmarca o checkbox de importante
            const importanteCheckbox = document.getElementById('evento-importante');
            if (importanteCheckbox) importanteCheckbox.checked = false;
            
            // Atualiza o título do formulário
            const formTitleElement = document.querySelector('.form-section h3');
            if (formTitleElement) {
                formTitleElement.textContent = 'Criar Novo Evento';
            }
            
            // Atualiza o texto do botão de submit
            const btnSalvar = formEvento.querySelector('button[type="submit"]');
            if (btnSalvar) {
                btnSalvar.innerHTML = '<i class="fas fa-save"></i> Salvar Evento';
                btnSalvar.disabled = false;
            }
            
            // Reseta o modo de edição
            editMode = false;
            
        } catch (error) {
            console.error('Erro ao resetar formulário:', error);
            showAlert('Ocorreu um erro ao tentar limpar o formulário.', 'error');
        }
    };

    // Função para obter valor seguro do campo do formulário
    const getFormValue = (fieldId) => {
        const field = document.getElementById(fieldId);
        return field ? field.value : '';
    };

    // Manipular envio do formulário
    formEvento.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        try {
            // Coletar dados do formulário
            const dataEvento = getFormValue('evento-data');
            const horaInicio = getFormValue('evento-inicio');
            const horaFim = getFormValue('evento-fim');
            
            // Formatar datas no formato ISO 8601 esperado pelo backend
            const startTime = dataEvento && horaInicio ? 
                `${dataEvento}T${horaInicio}:00` : null;
                
            const endTime = dataEvento && horaFim ? 
                `${dataEvento}T${horaFim}:00` : null;
            
            const formData = {
                titulo: getFormValue('evento-titulo'),
                descricao: getFormValue('evento-descricao') || '',
                local: getFormValue('evento-local'),
                palestrantes: getFormValue('evento-palestrantes') || '',
                tags: getFormValue('evento-tags') || 'sustentabilidade',
                start_time: startTime,
                end_time: endTime,
                latitude: parseFloat(getFormValue('evento-latitude')) || null,
                longitude: parseFloat(getFormValue('evento-longitude')) || null
            };
            
            console.log('Dados do formulário formatados:', JSON.stringify(formData, null, 2));

            // Validar dados
            const validarFormulario = (formData) => {
                // Implementar validação de dados aqui
            };
            validarFormulario(formData);

            const id = eventoIdInput?.value;
            const url = getEventUrl(id);
            const method = id ? 'PUT' : 'POST';
            
            console.log('Enviando para:', url, 'Método:', method, 'Dados:', formData);
            
            try {
                const response = await fetch(url, {
                    method: method,
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken,
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: JSON.stringify(formData),
                    credentials: 'same-origin'
                });
                
                let responseData = {};
                try {
                    responseData = await response.json();
                    console.log('Resposta do servidor:', responseData);
                } catch (e) {
                    console.error('Erro ao processar resposta JSON:', e);
                }
                
                if (!response.ok) {
                    const errorMessage = responseData.detail || 
                                       responseData.error || 
                                       responseData.message || 
                                       `Erro ${response.status}: ${response.statusText}`;
                    throw new Error(errorMessage);
                }
                
                showAlert(`Evento ${id ? 'atualizado' : 'criado'} com sucesso!`, 'success');
                
                // Recarregar a lista de eventos
                await carregarEventos();
                
                // Resetar o formulário
                resetarFormulario();
                
            } catch (error) {
                console.error('Erro na requisição:', {
                    error: error.message,
                    url: url,
                    method: method,
            }
        } catch (error) {
            console.error('Erro ao excluir evento:', error);
            showAlert(error.message || 'Erro ao excluir evento. Tente novamente.', 'error');
        } finally {
            toggleModal(false);
        }
    });
}

// Função para atualizar os contadores de eventos
async function atualizarContadores() {
    try {
        const response = await fetch('/api/eventos/contadores/');
        if (response.ok) {
            const data = await response.json();
            document.getElementById('total-eventos').textContent = data.total || 0;
            document.getElementById('eventos-hoje').textContent = data.hoje || 0;
            document.getElementById('eventos-destaque').textContent = data.destaque || 0;
        }
    } catch (error) {
        console.error('Erro ao carregar contadores:', error);
                formTitle.textContent = 'Editar Evento';
                const btnSalvar = formEvento.querySelector('button[type="submit"]');
                btnSalvar.innerHTML = '<i class="fas fa-save"></i> Salvar Alterações';
                editMode = true;
                
                // Extrair data e hora do evento
                const dataHoraInicio = evento.start_time ? new Date(evento.start_time) : null;
                const dataHoraFim = evento.end_time ? new Date(evento.end_time) : null;
                
                // Preencher campos do formulário
                document.getElementById('evento-id').value = evento.id;
                document.getElementById('evento-titulo').value = evento.titulo || '';
                document.getElementById('evento-descricao').value = evento.descricao || '';
                document.getElementById('evento-local').value = evento.local || '';
                document.getElementById('evento-tema').value = evento.tema || 'sustentabilidade';
                
                // Preencher data e hora
                if (dataHoraInicio) {
                    const dataFormatada = dataHoraInicio.toISOString().split('T')[0];
                    const horaFormatada = dataHoraInicio.toTimeString().substring(0, 5);
                    document.getElementById('evento-data').value = dataFormatada;
                    document.getElementById('evento-inicio').value = horaFormatada;
                }
                
                if (dataHoraFim) {
                    const horaFimFormatada = dataHoraFim.toTimeString().substring(0, 5);
                    document.getElementById('evento-fim').value = horaFimFormatada;
                }
                
                document.getElementById('evento-importante').checked = evento.importante || false;
                
                // Rolar até o formulário
                formEvento.scrollIntoView({ behavior: 'smooth' });
                
            } catch (error) {
                console.error('Erro:', error);
                showAlert('Erro ao carregar o evento. Tente novamente.', 'error');
            }
        }
    });
    
    // Pesquisar eventos
    const pesquisarEventos = (termo) => {
        if (!termo) {
            renderizarEventos();
            return;
        }
        
        const termoBusca = termo.toLowerCase();
        const eventosFiltrados = eventos.filter(evento => 
            evento.titulo.toLowerCase().includes(termoBusca) || 
            (evento.descricao && evento.descricao.toLowerCase().includes(termoBusca)) ||
            (evento.local && evento.local.toLowerCase().includes(termoBusca))
        );
        
        renderizarEventos(eventosFiltrados);
    };
    
    // Event listener para a barra de pesquisa
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            pesquisarEventos(e.target.value.trim());
        });
    }
    
    // Carregar eventos ao iniciar
    carregarEventos();
});