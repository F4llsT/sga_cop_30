document.addEventListener('DOMContentLoaded', () => {
    // Elementos do DOM
    const formEvento = document.querySelector('#form-evento');
    const listaEventos = document.getElementById('lista-eventos');
    const eventoIdInput = document.getElementById('evento-id');
    const searchInput = document.getElementById('search-input');
    
    // Verifica se o formulário existe
    if (!formEvento) {
        console.error('Formulário não encontrado');
        return;
    }
    
    // URLs da API - Ajustadas para corresponder exatamente às URLs do Django
    const API_BASE = '/meu-admin';
    const API_URL = `${API_BASE}/eventos/`;
    const API_EVENTOS = `${API_BASE}/api/eventos/`;
    
    // Função auxiliar para construir URLs da API
    const getEventUrl = (eventoId = '') => {
        if (eventoId) {
            return `${API_URL}${eventoId}/editar/`;
        }
        return `${API_URL}novo/`;
    };
    
    console.log('API URLs configuradas:', { API_URL, API_EVENTOS });
    
    let eventos = [];
    let editMode = false;
    
    // Obtém o token CSRF de forma segura
    let csrfToken = '';
    const csrfElement = document.querySelector('input[name="csrfmiddlewaretoken"]');
    if (csrfElement) {
        csrfToken = csrfElement.value;
    } else {
        console.error('Token CSRF não encontrado');
        return; // Não prosseguir sem o token CSRF
    }

    // Função para exibir mensagens de feedback
    const showAlert = (message, type = 'success') => {
        // Remove alertas existentes
        const existingAlert = document.querySelector('.alert');
        if (existingAlert) {
            existingAlert.remove();
        }
        
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type}`;
        alertDiv.textContent = message;
        
        // Insere o alerta após o cabeçalho
        const header = document.querySelector('.main-header');
        if (header) {
            header.insertAdjacentElement('afterend', alertDiv);
            
            // Remove o alerta após 5 segundos
            setTimeout(() => {
                alertDiv.remove();
            }, 5000);
        }
    };

    // Função para formatar data
    const formatDate = (dateString) => {
        const options = { year: 'numeric', month: '2-digit', day: '2-digit' };
        return new Date(dateString).toLocaleDateString('pt-BR', options);
    };

    // Função para formatar hora
    const formatTime = (timeString) => {
        if (!timeString) return '';
        const [hours, minutes] = timeString.split(':');
        return `${hours}:${minutes}`;
    };

    // Carregar eventos da API
    const carregarEventos = async () => {
        try {
            const response = await fetch(API_EVENTOS);
            if (!response.ok) throw new Error('Erro ao carregar eventos');
            
            eventos = await response.json();
            renderizarEventos();
        } catch (error) {
            console.error('Erro:', error);
            showAlert('Erro ao carregar eventos. Tente novamente mais tarde.', 'error');
        }
    };

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
                    data: formData
                });
                throw error; // Re-throw para ser capturado pelo catch externo
            }
            
        } catch (error) {
            console.error('Erro ao salvar evento:', error);
            const errorMessage = error.message || 'Erro ao processar o formulário. Verifique os dados e tente novamente.';
            showAlert(errorMessage, 'error');
        }
    });

    // Manipular cliques na lista de eventos
    listaEventos.addEventListener('click', async (e) => {
        const target = e.target.closest('button');
        if (!target) return;
        
        const card = target.closest('.event-card');
        const id = card?.dataset.id;
        
        if (!id) return;
        
        // Excluir evento
        if (target.classList.contains('delete-btn')) {
            if (confirm('Tem certeza que deseja excluir este evento? Esta ação não pode ser desfeita.')) {
                try {
                    const response = await fetch(`${API_EVENTOS}${id}/`, {
                        method: 'DELETE',
                        headers: {
                            'X-CSRFToken': csrfToken
                        }
                    });
                    
                    if (!response.ok) throw new Error('Erro ao excluir o evento');
                    
                    showAlert('Evento excluído com sucesso!');
                    await carregarEventos();
                    
                } catch (error) {
                    console.error('Erro:', error);
                    showAlert('Erro ao excluir o evento. Tente novamente.', 'error');
                }
            }
        }
        
        // Editar evento
        if (target.classList.contains('edit-btn')) {
            try {
                const response = await fetch(`${API_EVENTOS}${id}/`);
                if (!response.ok) throw new Error('Erro ao carregar evento');
                
                const evento = await response.json();
                
                // Preencher formulário com os dados do evento
                const formTitle = document.querySelector('.form-section h3');
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