/**
 * Gerenciamento de Eventos - Funcionalidades JavaScript
 * 
 * Este arquivo contém toda a lógica de frontend para o gerenciamento de eventos,
 * incluindo validação de formulário, integração com mapa e manipulação de eventos.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Elementos do DOM
    const formEvento = document.getElementById('form-evento');
    const inputTitulo = document.getElementById('evento-titulo');
    const inputDescricao = document.getElementById('evento-descricao');
    const inputDataInicio = document.getElementById('evento-data-inicio');
    const inputHoraInicio = document.getElementById('evento-inicio');
    const inputDataFim = document.getElementById('evento-data-fim');
    const inputHoraFim = document.getElementById('evento-fim');
    const inputLocal = document.getElementById('evento-local');
    const inputPalestrantes = document.getElementById('evento-palestrantes');
    const inputTags = document.getElementById('evento-tags');
    const inputImportante = document.getElementById('evento-importante');
    const inputLatitude = document.getElementById('evento-latitude');
    const inputLongitude = document.getElementById('evento-longitude');
    const btnLimpar = document.getElementById('btn-limpar');
    const btnAtualizar = document.getElementById('btn-atualizar');
    const btnLocalizar = document.getElementById('btn-localizar');
    const listaEventos = document.getElementById('lista-eventos');
    const searchInput = document.getElementById('search-input');
    
    // Estado da aplicação
    let mapa;
    let marcador;
    let eventoEditando = null;
    
    // Inicialização
    initMapa();
    carregarPalestrantes();
    carregarEventos();
    configurarEventos();
    
    /**
     * Inicializa o mapa usando Leaflet
     */
    function initMapa() {
        // Coordenadas padrão (São Paulo)
        const latPadrao = -23.550520;
        const lngPadrao = -46.633308;
        
        // Inicializa o mapa
        mapa = L.map('map').setView([latPadrao, lngPadrao], 13);
        
        // Adiciona o tile layer (OpenStreetMap)
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(mapa);
        
        // Adiciona um marcador inicial
        marcador = L.marker([latPadrao, lngPadrao], {draggable: true}).addTo(mapa);
        
        // Atualiza as coordenadas quando o marcador é arrastado
        marcador.on('dragend', function(e) {
            const posicao = marcador.getLatLng();
            inputLatitude.value = posicao.lat.toFixed(6);
            inputLongitude.value = posicao.lng.toFixed(6);
        });
        
        // Adiciona um marcador quando o mapa é clicado
        mapa.on('click', function(e) {
            const {lat, lng} = e.latlng;
            
            // Remove o marcador anterior se existir
            if (marcador) {
                mapa.removeLayer(marcador);
            }
            
            // Adiciona um novo marcador
            marcador = L.marker([lat, lng], {draggable: true}).addTo(mapa);
            
            // Atualiza os campos de latitude e longitude
            inputLatitude.value = lat.toFixed(6);
            inputLongitude.value = lng.toFixed(6);
            
            // Adiciona o evento de arrastar
            marcador.on('dragend', function(e) {
                const posicao = marcador.getLatLng();
                inputLatitude.value = posicao.lat.toFixed(6);
                inputLongitude.value = posicao.lng.toFixed(6);
            });
        });
    }
    
    /**
     * Carrega a lista de palestrantes via AJAX
     */
    function carregarPalestrantes() {
        // Simulação de chamada AJAX - substitua pela sua rota real
        fetch('/api/palestrantes/')
            .then(response => response.json())
            .then(palestrantes => {
                // Limpa o select
                inputPalestrantes.innerHTML = '';
                
                // Adiciona as opções
                palestrantes.forEach(palestrante => {
                    const option = document.createElement('option');
                    option.value = palestrante.id;
                    option.textContent = palestrante.nome;
                    inputPalestrantes.appendChild(option);
                });
                
                // Inicializa o select2 para melhor experiência do usuário
                $(inputPalestrantes).select2({
                    placeholder: 'Selecione os palestrantes',
                    allowClear: true,
                    width: '100%'
                });
            })
            .catch(error => {
                console.error('Erro ao carregar palestrantes:', error);
                mostrarAlerta('Erro ao carregar a lista de palestrantes', 'danger');
            });
    }
    
    /**
     * Carrega a lista de eventos
     */
    function carregarEventos() {
        // Mostra um indicador de carregamento
        listaEventos.innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Carregando...</span>
                </div>
                <p class="mt-2">Carregando eventos...</p>
            </div>
        `;
        
        // Simulação de chamada AJAX - substitua pela sua rota real
        fetch('/api/eventos/')
            .then(response => response.json())
            .then(eventos => {
                if (eventos.length === 0) {
                    listaEventos.innerHTML = `
                        <div class="text-center py-5 text-muted">
                            <i class="fas fa-calendar-alt fa-3x mb-3"></i>
                            <p>Nenhum evento agendado</p>
                        </div>
                    `;
                    return;
                }
                
                // Renderiza a lista de eventos
                renderizarEventos(eventos);
            })
            .catch(error => {
                console.error('Erro ao carregar eventos:', error);
                mostrarAlerta('Erro ao carregar os eventos', 'danger');
            });
    }
    
    /**
     * Renderiza a lista de eventos
     * @param {Array} eventos - Lista de eventos a serem renderizados
     */
    function renderizarEventos(eventos) {
        listaEventos.innerHTML = '';
        
        eventos.forEach(evento => {
            const dataInicio = new Date(evento.data_inicio);
            const dataFim = new Date(evento.data_fim);
            const agora = new Date();
            const status = agora < dataInicio ? 'agendado' : agora > dataFim ? 'encerrado' : 'em-andamento';
            
            const eventoElement = document.createElement('div');
            eventoElement.className = `evento-card ${status} ${evento.importante ? 'importante' : ''}`;
            eventoElement.dataset.id = evento.id;
            eventoElement.innerHTML = `
                <div class="evento-header">
                    <h4 class="evento-titulo">${evento.titulo}</h4>
                    <span class="evento-status badge bg-${getStatusBadgeClass(status)}">${getStatusText(status)}</span>
                </div>
                <div class="evento-corpo">
                    <div class="evento-descricao">${evento.descricao || '<em>Sem descrição</em>'}</div>
                    <div class="evento-info">
                        <div><i class="far fa-calendar-alt"></i> ${formatarData(dataInicio)} - ${formatarData(dataFim)}</div>
                        <div><i class="far fa-clock"></i> ${formatarHora(dataInicio)} - ${formatarHora(dataFim)}</div>
                        ${evento.local ? `<div><i class="fas fa-map-marker-alt"></i> ${evento.local}</div>` : ''}
                    </div>
                    ${evento.palestrantes && evento.palestrantes.length > 0 ? `
                        <div class="evento-palestrantes">
                            <i class="fas fa-users"></i>
                            ${evento.palestrantes.map(p => p.nome).join(', ')}
                        </div>
                    ` : ''}
                    ${evento.tags ? `
                        <div class="evento-tags">
                            ${evento.tags.split(',').map(tag => `<span class="badge bg-secondary">${tag.trim()}</span>`).join('')}
                        </div>
                    ` : ''}
                </div>
                <div class="evento-acoes">
                    <button class="btn btn-sm btn-outline-primary btn-editar" data-id="${evento.id}">
                        <i class="fas fa-edit"></i> Editar
                    </button>
                    <button class="btn btn-sm btn-outline-danger btn-excluir" data-id="${evento.id}">
                        <i class="fas fa-trash-alt"></i> Excluir
                    </button>
                </div>
            `;
            
            listaEventos.appendChild(eventoElement);
        });
        
        // Adiciona os eventos aos botões
        document.querySelectorAll('.btn-editar').forEach(btn => {
            btn.addEventListener('click', function() {
                const eventoId = this.dataset.id;
                editarEvento(eventoId);
            });
        });
        
        document.querySelectorAll('.btn-excluir').forEach(btn => {
            btn.addEventListener('click', function() {
                const eventoId = this.dataset.id;
                confirmarExclusao(eventoId);
            });
        });
    }
    
    /**
     * Preenche o formulário com os dados de um evento para edição
     * @param {string} eventoId - ID do evento a ser editado
     */
    function editarEvento(eventoId) {
        // Simulação de chamada AJAX - substitua pela sua rota real
        fetch(`/api/eventos/${eventoId}/`)
            .then(response => response.json())
            .then(evento => {
                // Preenche o formulário com os dados do evento
                eventoEditando = evento.id;
                inputTitulo.value = evento.titulo;
                inputDescricao.value = evento.descricao || '';
                
                // Formata as datas
                const dataInicio = new Date(evento.data_inicio);
                const dataFim = new Date(evento.data_fim);
                
                inputDataInicio.value = formatarDataParaInput(dataInicio);
                inputHoraInicio.value = formatarHoraParaInput(dataInicio);
                inputDataFim.value = formatarDataParaInput(dataFim);
                inputHoraFim.value = formatarHoraParaInput(dataFim);
                
                inputLocal.value = evento.local || '';
                inputTags.value = evento.tags || '';
                inputImportante.checked = evento.importante || false;
                
                // Define a posição do mapa
                if (evento.latitude && evento.longitude) {
                    inputLatitude.value = evento.latitude;
                    inputLongitude.value = evento.longitude;
                    
                    // Atualiza o marcador no mapa
                    const latLng = [parseFloat(evento.latitude), parseFloat(evento.longitude)];
                    if (marcador) {
                        mapa.removeLayer(marcador);
                    }
                    marcador = L.marker(latLng, {draggable: true}).addTo(mapa);
                    mapa.setView(latLng, 15);
                    
                    // Atualiza as coordenadas quando o marcador é arrastado
                    marcador.on('dragend', function(e) {
                        const posicao = marcador.getLatLng();
                        inputLatitude.value = posicao.lat.toFixed(6);
                        inputLongitude.value = posicao.lng.toFixed(6);
                    });
                }
                
                // Seleciona os palestrantes
                if (evento.palestrantes && evento.palestrantes.length > 0) {
                    const palestrantesIds = evento.palestrantes.map(p => p.id);
                    $(inputPalestrantes).val(palestrantesIds).trigger('change');
                } else {
                    $(inputPalestrantes).val(null).trigger('change');
                }
                
                // Atualiza o botão de submit
                const btnSubmit = formEvento.querySelector('button[type="submit"]');
                btnSubmit.innerHTML = '<i class="fas fa-save"></i> Atualizar Evento';
                
                // Rola até o formulário
                formEvento.scrollIntoView({ behavior: 'smooth' });
                
                // Mostra mensagem
                mostrarAlerta('Preencha os campos e clique em Atualizar para salvar as alterações', 'info');
            })
            .catch(error => {
                console.error('Erro ao carregar evento:', error);
                mostrarAlerta('Erro ao carregar os dados do evento', 'danger');
            });
    }
    
    /**
     * Mostra um modal de confirmação antes de excluir um evento
     * @param {string} eventoId - ID do evento a ser excluído
     */
    function confirmarExclusao(eventoId) {
        // Encontra o título do evento para mostrar no modal
        const eventoElement = document.querySelector(`.evento-card[data-id="${eventoId}"]`);
        const tituloEvento = eventoElement ? eventoElement.querySelector('.evento-titulo').textContent : 'este evento';
        
        // Atualiza o modal de confirmação
        const modal = new bootstrap.Modal(document.getElementById('confirm-modal'));
        const modalTitle = document.querySelector('#confirm-modal .modal-title');
        const modalBody = document.querySelector('#confirm-modal .modal-body');
        const btnConfirmar = document.querySelector('#confirm-modal .btn-confirmar');
        
        modalTitle.textContent = 'Confirmar Exclusão';
        modalBody.innerHTML = `Tem certeza que deseja excluir o evento <strong>${tituloEvento}</strong>? Esta ação não pode ser desfeita.`;
        
        // Remove eventos anteriores
        const novoBtn = btnConfirmar.cloneNode(true);
        btnConfirmar.parentNode.replaceChild(novoBtn, btnConfirmar);
        
        // Adiciona o evento de confirmação
        novoBtn.addEventListener('click', function() {
            excluirEvento(eventoId);
            modal.hide();
        });
        
        // Mostra o modal
        modal.show();
    }
    
    /**
     * Exclui um evento
     * @param {string} eventoId - ID do evento a ser excluído
     */
    function excluirEvento(eventoId) {
        // Simulação de chamada AJAX - substitua pela sua rota real
        fetch(`/api/eventos/${eventoId}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro ao excluir o evento');
            }
            return response.json();
        })
        .then(() => {
            mostrarAlerta('Evento excluído com sucesso!', 'success');
            carregarEventos();
        })
        .catch(error => {
            console.error('Erro ao excluir evento:', error);
            mostrarAlerta('Erro ao excluir o evento', 'danger');
        });
    }
    
    /**
     * Configura os eventos do formulário
     */
    function configurarEventos() {
        // Evento de envio do formulário
        formEvento.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Validação básica
            if (!validarFormulario()) {
                return;
            }
            
            // Prepara os dados do evento
            const dadosEvento = {
                titulo: inputTitulo.value.trim(),
                descricao: inputDescricao.value.trim(),
                data_inicio: `${inputDataInicio.value}T${inputHoraInicio.value}:00`,
                data_fim: `${inputDataFim.value}T${inputHoraFim.value}:00`,
                local: inputLocal.value.trim(),
                tags: inputTags.value.trim(),
                importante: inputImportante.checked,
                palestrantes: Array.from(inputPalestrantes.selectedOptions).map(opt => parseInt(opt.value)),
                latitude: inputLatitude.value ? parseFloat(inputLatitude.value) : null,
                longitude: inputLongitude.value ? parseFloat(inputLongitude.value) : null
            };
            
            // Determina o método HTTP e a URL
            const metodo = eventoEditando ? 'PUT' : 'POST';
            const url = eventoEditando 
                ? `/api/eventos/${eventoEditando}/` 
                : '/api/eventos/';
            
            // Envia os dados
            fetch(url, {
                method: metodo,
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(dadosEvento)
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw err; });
                }
                return response.json();
            })
            .then(() => {
                const mensagem = eventoEditando 
                    ? 'Evento atualizado com sucesso!' 
                    : 'Evento criado com sucesso!';
                
                mostrarAlerta(mensagem, 'success');
                limparFormulario();
                carregarEventos();
            })
            .catch(error => {
                console.error('Erro ao salvar evento:', error);
                const mensagem = error.mensagem || 'Erro ao salvar o evento. Por favor, tente novamente.';
                mostrarAlerta(mensagem, 'danger');
            });
        });
        
        // Evento do botão limpar
        btnLimpar.addEventListener('click', limparFormulario);
        
        // Evento do botão atualizar
        btnAtualizar.addEventListener('click', carregarEventos);
        
        // Evento do botão de localização
        btnLocalizar.addEventListener('click', function() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    function(position) {
                        const { latitude, longitude } = position.coords;
                        
                        // Atualiza os campos
                        inputLatitude.value = latitude.toFixed(6);
                        inputLongitude.value = longitude.toFixed(6);
                        
                        // Atualiza o mapa
                        if (marcador) {
                            mapa.removeLayer(marcador);
                        }
                        
                        marcador = L.marker([latitude, longitude], {draggable: true}).addTo(mapa);
                        mapa.setView([latitude, longitude], 15);
                        
                        // Atualiza as coordenadas quando o marcador é arrastado
                        marcador.on('dragend', function(e) {
                            const posicao = marcador.getLatLng();
                            inputLatitude.value = posicao.lat.toFixed(6);
                            inputLongitude.value = posicao.lng.toFixed(6);
                        });
                        
                        // Busca o endereço (opcional)
                        buscarEnderecoPorCoordenadas(latitude, longitude);
                    },
                    function(error) {
                        console.error('Erro ao obter localização:', error);
                        mostrarAlerta('Não foi possível obter sua localização. Por favor, insira as coordenadas manualmente.', 'warning');
                    },
                    { enableHighAccuracy: true, timeout: 5000, maximumAge: 0 }
                );
            } else {
                mostrarAlerta('Seu navegador não suporta geolocalização. Por favor, insira as coordenadas manualmente.', 'warning');
            }
        });
        
        // Evento de busca
        searchInput.addEventListener('input', function() {
            const termo = this.value.toLowerCase();
            const cards = document.querySelectorAll('.evento-card');
            
            cards.forEach(card => {
                const texto = card.textContent.toLowerCase();
                card.style.display = texto.includes(termo) ? 'block' : 'none';
            });
        });
    }
    
    /**
     * Valida o formulário antes do envio
     * @returns {boolean} True se o formulário for válido, False caso contrário
     */
    function validarFormulario() {
        // Validação do título
        if (!inputTitulo.value.trim()) {
            mostrarAlerta('Por favor, insira um título para o evento', 'warning');
            inputTitulo.focus();
            return false;
        }
        
        // Validação das datas
        const dataInicio = new Date(`${inputDataInicio.value}T${inputHoraInicio.value}`);
        const dataFim = new Date(`${inputDataFim.value}T${inputHoraFim.value}`);
        
        if (dataFim <= dataInicio) {
            mostrarAlerta('A data/hora de término deve ser posterior à data/hora de início', 'warning');
            inputDataFim.focus();
            return false;
        }
        
        // Validação do local
        if (!inputLocal.value.trim()) {
            mostrarAlerta('Por favor, informe o local do evento', 'warning');
            inputLocal.focus();
            return false;
        }
        
        return true;
    }
    
    /**
     * Limpa o formulário
     */
    function limparFormulario() {
        formEvento.reset();
        eventoEditando = null;
        
        // Limpa o select de palestrantes
        $(inputPalestrantes).val(null).trigger('change');
        
        // Atualiza o botão de submit
        const btnSubmit = formEvento.querySelector('button[type="submit"]');
        btnSubmit.innerHTML = '<i class="fas fa-save"></i> Salvar Evento';
        
        // Remove a classe de validação
        formEvento.querySelectorAll('.is-invalid').forEach(el => {
            el.classList.remove('is-invalid');
        });
        
        // Foca no primeiro campo
        inputTitulo.focus();
    }
    
    /**
     * Busca um endereço a partir de coordenadas (geocodificação reversa)
     * @param {number} latitude - Latitude
     * @param {number} longitude - Longitude
     */
    function buscarEnderecoPorCoordenadas(latitude, longitude) {
        // Usando a API de Geocodificação do OpenStreetMap (Nominatim)
        fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}&zoom=18&addressdetails=1`)
            .then(response => response.json())
            .then(data => {
                if (data.display_name) {
                    // Preenche o campo de local com o endereço encontrado
                    inputLocal.value = data.display_name;
                }
            })
            .catch(error => {
                console.error('Erro ao buscar endereço:', error);
            });
    }
    
    /**
     * Mostra uma mensagem de alerta
     * @param {string} mensagem - Mensagem a ser exibida
     * @param {string} tipo - Tipo de alerta (success, danger, warning, info)
     */
    function mostrarAlerta(mensagem, tipo = 'info') {
        // Remove alertas anteriores
        const alertasAnteriores = document.querySelectorAll('.alert-dismissible');
        alertasAnteriores.forEach(alerta => alerta.remove());
        
        // Cria o elemento do alerta
        const alerta = document.createElement('div');
        alerta.className = `alert alert-${tipo} alert-dismissible fade show`;
        alerta.role = 'alert';
        alerta.innerHTML = `
            ${mensagem}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Fechar"></button>
        `;
        
        // Adiciona o alerta ao início do conteúdo principal
        const mainContent = document.querySelector('.main-content');
        mainContent.insertBefore(alerta, mainContent.firstChild);
        
        // Remove o alerta após 5 segundos
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alerta);
            bsAlert.close();
        }, 5000);
    }
    
    // Funções auxiliares
    
    /**
     * Obtém o valor de um cookie pelo nome
     * @param {string} name - Nome do cookie
     * @returns {string|null} Valor do cookie ou null se não encontrado
     */
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
    
    /**
     * Formata uma data para exibição
     * @param {Date} data - Objeto Date a ser formatado
     * @returns {string} Data formatada
     */
    function formatarData(data) {
        return data.toLocaleDateString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        });
    }
    
    /**
     * Formata uma hora para exibição
     * @param {Date} data - Objeto Date contendo a hora
     * @returns {string} Hora formatada
     */
    function formatarHora(data) {
        return data.toLocaleTimeString('pt-BR', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }
    
    /**
     * Formata uma data para o input type="date"
     * @param {Date} data - Objeto Date a ser formatado
     * @returns {string} Data no formato YYYY-MM-DD
     */
    function formatarDataParaInput(data) {
        const ano = data.getFullYear();
        const mes = String(data.getMonth() + 1).padStart(2, '0');
        const dia = String(data.getDate()).padStart(2, '0');
        return `${ano}-${mes}-${dia}`;
    }
    
    /**
     * Formata uma hora para o input type="time"
     * @param {Date} data - Objeto Date contendo a hora
     * @returns {string} Hora no formato HH:MM
     */
    function formatarHoraParaInput(data) {
        const horas = String(data.getHours()).padStart(2, '0');
        const minutos = String(data.getMinutes()).padStart(2, '0');
        return `${horas}:${minutos}`;
    }
    
    /**
     * Retorna a classe CSS para o badge de status
     * @param {string} status - Status do evento
     * @returns {string} Classe CSS
     */
    function getStatusBadgeClass(status) {
        const classes = {
            'agendado': 'bg-primary',
            'em-andamento': 'bg-success',
            'encerrado': 'bg-secondary'
        };
        return classes[status] || 'bg-secondary';
    }
    
    /**
     * Retorna o texto do status formatado
     * @param {string} status - Status do evento
     * @returns {string} Texto formatado
     */
    function getStatusText(status) {
        const textos = {
            'agendado': 'Agendado',
            'em-andamento': 'Em Andamento',
            'encerrado': 'Encerrado'
        };
        return textos[status] || status;
    }
});
