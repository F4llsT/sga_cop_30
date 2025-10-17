// apps/admin_personalizado/static/admin_personalizado/js/eventos.js

document.addEventListener('DOMContentLoaded', () => {
    // Elementos do DOM
    const formEvento = document.getElementById('form-evento');
    const listaEventos = document.getElementById('lista-eventos');
    const formTitle = document.getElementById('form-title');
    const eventoIdInput = document.getElementById('evento-id');
    const btnLimpar = document.getElementById('btn-limpar');
    const btnAtualizar = document.getElementById('btn-atualizar');
    const searchInput = document.getElementById('search-input');

    // Elementos do formulário
    const inputTitulo = document.getElementById('evento-titulo');
    const inputDescricao = document.getElementById('evento-descricao');
    const inputDataInicio = document.getElementById('evento-data-inicio');
    const inputHoraInicio = document.getElementById('evento-hora-inicio');
    const inputDataFim = document.getElementById('evento-data-fim');
    const inputHoraFim = document.getElementById('evento-hora-fim');
    const inputLocal = document.getElementById('evento-local');
    const inputPalestrantes = document.getElementById('evento-palestrantes');
    const inputTags = document.getElementById('evento-tags');
    const inputImportante = document.getElementById('evento-importante');
    const inputLatitude = document.getElementById('evento-latitude');
    const inputLongitude = document.getElementById('evento-longitude');
    const btnLocalizar = document.getElementById('btn-localizar');

    // Variáveis de estado
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
    // Na função initMapa()
    function initMapa() {
        // Coordenadas padrão (São Paulo)
        const latPadrao = -23.550520;
        const lngPadrao = -46.633308;
        
        // Inicializa o mapa
        mapa = L.map('map', {
            zoomControl: false  // Vamos adicionar o controle de zoom manualmente
        }).setView([latPadrao, lngPadrao], 13);
        
        // Adiciona o tile layer (OpenStreetMap)
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 19
        }).addTo(mapa);
        
        // Adiciona controles de zoom
        L.control.zoom({
            position: 'topright'
        }).addTo(mapa);
        
        // Configura o marcador
        marcador = L.marker([latPadrao, lngPadrao], {
            draggable: true
        }).addTo(mapa);
        
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
        });

        // Força o redesenho do mapa quando a janela for redimensionada
        window.addEventListener('resize', function() {
            setTimeout(() => {
                mapa.invalidateSize(true);
            }, 100);
        });
    }

    // Na função carregarPalestrantes()
    function carregarPalestrantes() {
        fetch('/api/palestrantes/')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Erro HTTP: ${response.status}`);
                }
                return response.json().catch(() => {
                    throw new Error('Resposta da API não é um JSON válido');
                });
            })
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
                
                // Inicializa o select2
                $(inputPalestrantes).select2({
                    placeholder: 'Selecione os palestrantes',
                    allowClear: true,
                    width: '100%'
                });
            })
            .catch(error => {
                console.error('Erro ao carregar palestrantes:', error);
                mostrarAlerta('Erro ao carregar a lista de palestrantes. Verifique o console para mais detalhes.', 'danger');
            });
    }

    // Na função carregarEventos()
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
        
        fetch('/api/eventos/')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Erro HTTP: ${response.status}`);
                }
                return response.json().catch(() => {
                    throw new Error('Resposta da API não é um JSON válido');
                });
            })
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
                
                renderizarEventos(eventos);
            })
            .catch(error => {
                console.error('Erro ao carregar eventos:', error);
                listaEventos.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        Erro ao carregar eventos. Por favor, recarregue a página ou tente novamente mais tarde.
                    </div>
                `;
            });
    }

    // Adicione esta função para forçar o redesenho do mapa quando necessário
    function ajustarMapa() {
        setTimeout(() => {
            if (mapa) {
                mapa.invalidateSize(true);
            }
        }, 300);
    }

    // Chame esta função quando o modal ou aba com o mapa for aberta
    // Por exemplo, se você estiver usando abas ou modais:
    document.querySelectorAll('[data-bs-toggle="tab"], [data-bs-toggle="modal"]').forEach(element => {
        element.addEventListener('shown.bs.tab shown.bs.modal', ajustarMapa);
    });

    /**
     * Renderiza a lista de eventos
     */
    function renderizarEventos(eventos) {
        listaEventos.innerHTML = '';
        
        if (eventos.length === 0) {
            listaEventos.innerHTML = `
                <div class="text-center py-5 text-muted">
                    <i class="fas fa-calendar-alt fa-3x mb-3"></i>
                    <p>Nenhum evento agendado</p>
                </div>
            `;
            return;
        }

        eventos.forEach(evento => {
            const eventoElement = document.createElement('div');
            eventoElement.className = `event-card ${evento.importante ? 'importante' : ''}`;
            eventoElement.dataset.id = evento.id;
            
            const dataInicio = new Date(evento.start_time);
            const dataFim = new Date(evento.end_time);
            const agora = new Date();
            const status = agora < dataInicio ? 'agendado' : agora > dataFim ? 'encerrado' : 'em-andamento';
            
            eventoElement.innerHTML = `
                <div class="event-details">
                    <h4>${evento.titulo}</h4>
                    <p>${evento.descricao || '<em>Sem descrição</em>'}</p>
                    <div class="event-meta">
                        <span><i class="fas fa-calendar-day"></i> ${formatarData(dataInicio)} - ${formatarData(dataFim)}</span>
                        <span><i class="fas fa-clock"></i> ${formatarHora(dataInicio)} - ${formatarHora(dataFim)}</span>
                        ${evento.local ? `<span><i class="fas fa-map-marker-alt"></i> ${evento.local}</span>` : ''}
                        <span class="badge ${getStatusBadgeClass(status)}">${getStatusText(status)}</span>
                    </div>
                    ${evento.tags ? `
                        <div class="event-tags mt-2">
                            ${evento.tags.split(',').map(tag => 
                                `<span class="badge bg-secondary me-1">${tag.trim()}</span>`
                            ).join('')}
                        </div>
                    ` : ''}
                </div>
                <div class="event-actions">
                    <button class="btn btn-sm btn-outline-primary edit-btn" title="Editar">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger delete-btn" title="Excluir">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;
            
            listaEventos.appendChild(eventoElement);
        });

        // Adiciona os eventos de clique após renderizar
        adicionarEventosBotoes();
    }

    /**
     * Configura os eventos do formulário
     */
    function configurarEventos() {
        // Evento de envio do formulário
        formEvento.addEventListener('submit', function(e) {
            e.preventDefault();
            
            if (!validarFormulario()) {
                return;
            }
            
            const dadosEvento = {
                titulo: inputTitulo.value.trim(),
                descricao: inputDescricao.value.trim(),
                data_inicio: inputDataInicio.value,
                hora_inicio: inputHoraInicio.value,
                data_fim: inputDataFim.value,
                hora_fim: inputHoraFim.value,
                local: inputLocal.value.trim(),
                tags: inputTags.value.trim(),
                importante: inputImportante.checked,
                palestrantes: Array.from(inputPalestrantes.selectedOptions).map(opt => parseInt(opt.value)),
                latitude: inputLatitude.value || null,
                longitude: inputLongitude.value || null
            };
            
            const metodo = eventoEditando ? 'PUT' : 'POST';
            const url = eventoEditando 
                ? `/api/eventos/${eventoEditando}/` 
                : '/api/eventos/';
            
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
                const mensagem = error.detail || error.error || 'Erro ao salvar o evento. Por favor, tente novamente.';
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
                    },
                    function(error) {
                        console.error('Erro ao obter localização:', error);
                        mostrarAlerta('Não foi possível obter sua localização', 'warning');
                    }
                );
            } else {
                mostrarAlerta('Seu navegador não suporta geolocalização', 'warning');
            }
        });

        // Evento de busca
        searchInput.addEventListener('input', function(e) {
            const termo = e.target.value.toLowerCase();
            const cards = document.querySelectorAll('.event-card');
            
            cards.forEach(card => {
                const texto = card.textContent.toLowerCase();
                card.style.display = texto.includes(termo) ? '' : 'none';
            });
        });
    }

    /**
     * Adiciona eventos aos botões de editar e excluir
     */
    function adicionarEventosBotoes() {
        // Evento de edição
        document.querySelectorAll('.edit-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const card = this.closest('.event-card');
                const eventoId = card.dataset.id;
                editarEvento(eventoId);
            });
        });

        // Evento de exclusão
        document.querySelectorAll('.delete-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const card = this.closest('.event-card');
                const eventoId = card.dataset.id;
                confirmarExclusao(eventoId);
            });
        });
    }

    /**
     * Preenche o formulário para edição
     */
    function editarEvento(eventoId) {
        fetch(`/api/eventos/${eventoId}/`)
            .then(response => response.json())
            .then(evento => {
                eventoEditando = evento.id;
                
                // Preenche o formulário
                inputTitulo.value = evento.titulo || '';
                inputDescricao.value = evento.descricao || '';
                inputLocal.value = evento.local || '';
                inputTags.value = evento.tags || '';
                inputImportante.checked = evento.importante || false;
                
                // Preenche as datas
                if (evento.start_time) {
                    const dataInicio = new Date(evento.start_time);
                    inputDataInicio.value = formatarDataParaInput(dataInicio);
                    inputHoraInicio.value = formatarHoraParaInput(dataInicio);
                }
                
                if (evento.end_time) {
                    const dataFim = new Date(evento.end_time);
                    inputDataFim.value = formatarDataParaInput(dataFim);
                    inputHoraFim.value = formatarHoraParaInput(dataFim);
                }
                
                // Preenche as coordenadas
                if (evento.latitude && evento.longitude) {
                    inputLatitude.value = evento.latitude;
                    inputLongitude.value = evento.longitude;
                    
                    // Atualiza o mapa
                    if (marcador) {
                        mapa.removeLayer(marcador);
                    }
                    
                    const latLng = [parseFloat(evento.latitude), parseFloat(evento.longitude)];
                    marcador = L.marker(latLng, {draggable: true}).addTo(mapa);
                    mapa.setView(latLng, 15);
                }
                
                // Preenche os palestrantes
                if (evento.palestrantes) {
                    const palestrantesIds = evento.palestrantes.split(',').map(id => id.trim());
                    $(inputPalestrantes).val(palestrantesIds).trigger('change');
                }
                
                // Rola até o formulário
                formEvento.scrollIntoView({ behavior: 'smooth' });
                formTitle.textContent = 'Editar Evento';
            })
            .catch(error => {
                console.error('Erro ao carregar evento:', error);
                mostrarAlerta('Erro ao carregar os dados do evento', 'danger');
            });
    }

    /**
     * Confirma a exclusão de um evento
     */
    function confirmarExclusao(eventoId) {
        if (confirm('Tem certeza que deseja excluir este evento?')) {
            fetch(`/api/eventos/${eventoId}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                },
                credentials: 'same-origin'
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Erro ao excluir evento');
                }
                return response.json();
            })
            .then(data => {
                mostrarAlerta('Evento excluído com sucesso!', 'success');
                carregarEventos();
            })
            .catch(error => {
                console.error('Erro ao excluir evento:', error);
                mostrarAlerta('Erro ao excluir o evento', 'danger');
            });
        }
    };

    // Inicialização
    initMapa();
    carregarPalestrantes();
    carregarEventos();
    configurarEventos();
    adicionarEventosBotoes();
});

// Função auxiliar para obter cookie
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

// Função para mostrar alertas
function mostrarAlerta(mensagem, tipo = 'info') {
    const alerta = document.createElement('div');
    alerta.className = `alert alert-${tipo} alert-dismissible fade show`;
    alerta.role = 'alert';
    alerta.innerHTML = `
        ${mensagem}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Fechar"></button>
    `;
    
    const container = document.querySelector('.container') || document.body;
    container.insertBefore(alerta, container.firstChild);
    
    // Remove o alerta após 5 segundos
    setTimeout(() => {
        alerta.remove();
    }, 5000);
}


// Código temporário para debug
async function testarAPIs() {
    try {
        console.log('Testando API de Eventos:');
        const eventosRes = await fetch('/api/eventos/');
        const eventosText = await eventosRes.text();
        console.log('Status:', eventosRes.status);
        console.log('Headers:', Object.fromEntries([...eventosRes.headers.entries()]));
        console.log('Resposta:', eventosText);
        
        console.log('\nTestando API de Palestrantes:');
        const palestrantesRes = await fetch('/api/palestrantes/');
        const palestrantesText = await palestrantesRes.text();
        console.log('Status:', palestrantesRes.status);
        console.log('Headers:', Object.fromEntries([...palestrantesRes.headers.entries()]));
        console.log('Resposta:', palestrantesText);
    } catch (error) {
        console.error('Erro ao testar APIs:', error);
    }
}

// Descomente a linha abaixo para testar as APIs
// testarAPIs();