/**
 * eventos-new.js
 * Script para gerenciamento de eventos no painel administrativo
 * Versão: 1.0.0
 */

// Verifica se a variável já foi declarada
if (typeof mapaInicializado === 'undefined') {
    var mapaInicializado = false;
}

// Inicialização quando o DOM estiver pronto
const init = () => {
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
    const inputPalestrante = document.getElementById('palestrante');
    const inputTags = document.getElementById('evento-tags');
    const inputImportante = document.getElementById('evento-importante');
    const inputLatitude = document.getElementById('evento-latitude');
    const inputLongitude = document.getElementById('evento-longitude');
    const btnLocalizar = document.getElementById('btn-localizar');

    // Variáveis de estado
    let mapa;
    let marcador;
    let eventoEditando = null;

    // Evita erro caso haja chamadas antigas
    function configurarEventos() {}

    // Inicialização
    const init = () => {
        // Espera um pouco para garantir que o DOM esteja totalmente carregado
        setTimeout(() => {
            initMapa();
            carregarEventos();
            configurarEventos();
            
            // Redesenha o mapa quando a aba se tornar visível
            document.addEventListener('visibilitychange', () => {
                if (!document.hidden && mapa) {
                    setTimeout(() => {
                        mapa.invalidateSize({animate: true});
                    }, 300);
                }
            });
            
            // Redesenha o mapa quando o usuário interagir com o painel
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    if (mutation.attributeName === 'class') {
                        const isCollapsed = document.body.classList.contains('sidebar-collapse');
                        if (mapa) {
                            setTimeout(() => {
                                mapa.invalidateSize({animate: true});
                            }, 300);
                        }
                    }
                });
            });
            
            // Observa mudanças no body para detectar colapso/expansão do menu
            observer.observe(document.body, {
                attributes: true,
                attributeFilter: ['class']
            });
            
        }, 100);
    };
    
    // Inicia a aplicação
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // Redesenha o mapa quando o painel for expandido/recolhido
    document.addEventListener('click', function(e) {
        // Verifica se o clique foi em um botão que pode expandir/recolher o painel
        const isToggleButton = e.target.matches('[data-widget="pushmenu"], [data-widget="pushmenu"] *');
        
        if (isToggleButton && mapa) {
            // Pequeno atraso para permitir que a animação do painel seja concluída
            setTimeout(() => {
                if (mapa) {
                    mapa.invalidateSize({animate: true});
                }
            }, 350);
        }
    });

    /**
     * Inicializa o mapa usando Leaflet
     */
    function initMapa() {
        // Verifica se o mapa já foi inicializado
        if (mapaInicializado) {
            // Se já estiver inicializado, apenas atualiza o tamanho
            if (mapa) {
                // Força um redesenho completo do mapa
                setTimeout(() => {
                    try {
                        mapa.invalidateSize({animate: true, pan: false});
                        // Força um redesenho dos tiles
                        const zoom = mapa.getZoom();
                        mapa.setZoom(zoom + 0.1, {animate: false});
                        setTimeout(() => {
                            mapa.setZoom(zoom, {animate: false});
                        }, 10);
                    } catch (e) {
                        console.warn('Erro ao redesenhar o mapa:', e);
                    }
                }, 100);
            }
            return;
        }

        // Coordenadas padrão (Belém do Pará)
        const latPadrao = -1.4558;
        const lngPadrao = -48.5039;
        
        try {
            const mapElement = document.getElementById('map');
            if (!mapElement) {
                console.error('Elemento do mapa não encontrado');
                return;
            }

            // Remove instância anterior do mapa, se existir
            if (mapa) {
                mapa.off();
                mapa.remove();
            }

            // Garante que o contêiner do mapa esteja visível
            mapElement.style.visibility = 'hidden';
            
            // Pequeno atraso para garantir que o DOM esteja pronto
            setTimeout(() => {
                try {
                    // Inicializa o mapa com configurações otimizadas
                    mapa = L.map('map', {
                        zoomControl: false,
                        preferCanvas: true,
                        tap: false,
                        zoomSnap: 0.1,
                        zoomDelta: 0.1,
                        wheelPxPerZoomLevel: 60,
                        renderer: L.canvas(),
                        zoom: 13,
                        center: [latPadrao, lngPadrao]
                    });
                    
                    // Adiciona o tile layer (OpenStreetMap) com configurações otimizadas
                    const tileLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                        attribution: '© OpenStreetMap contributors',
                        maxZoom: 19,
                        minZoom: 2,
                        noWrap: true,
                        updateWhenIdle: false, // Atualiza imediatamente
                        reuseTiles: true,     // Reutiliza tiles para melhor desempenho
                        updateWhenZooming: false, // Evita atualização durante o zoom
                        updateInterval: 100,   // Intervalo de atualização em ms
                        zIndex: 1
                    }).addTo(mapa);
                    
                    // Força o carregamento dos tiles
                    tileLayer.on('loading', function() {
                        // Adiciona uma classe de carregamento
                        const mapElement = document.getElementById('map');
                        if (mapElement) {
                            mapElement.classList.add('map-loading');
                        }
                    });
                    
                    tileLayer.on('load', function() {
                        // Remove a classe de carregamento quando os tiles forem carregados
                        const mapElement = document.getElementById('map');
                        if (mapElement) {
                            mapElement.classList.remove('map-loading');
                        }
                    });
                    
                    // Adiciona controles de zoom
                    L.control.zoom({
                        position: 'topright',
                        zoomInTitle: 'Aproximar',
                        zoomOutTitle: 'Afastar'
                    }).addTo(mapa);
                    
                    // Configura o marcador inicial
                    configurarMarcador(latPadrao, lngPadrao);
                    
                    // Adiciona um marcador quando o mapa é clicado
                    mapa.on('click', function(e) {
                        const {lat, lng} = e.latlng;
                        configurarMarcador(lat, lng);
                        atualizarCoordenadas(lat, lng);
                    });
                    
                    // Ajusta o mapa quando a janela for redimensionada
                    const resizeObserver = new ResizeObserver(debounce(() => {
                        if (mapa) {
                            setTimeout(() => {
                                mapa.invalidateSize({animate: true});
                            }, 100);
                        }
                    }, 250));
                    
                    // Observa mudanças no contêiner do mapa
                    resizeObserver.observe(mapElement);
                    
                    // Torna o mapa visível após a inicialização
                    mapElement.style.visibility = 'visible';
                    
                    // Força um redesenho do mapa
                    setTimeout(() => {
                        if (mapa) {
                            mapa.invalidateSize({animate: true});
                        }
                    }, 300);
                    
                    mapaInicializado = true;
                    console.log('Mapa inicializado com sucesso');
                    
                } catch (error) {
                    console.error('Erro ao inicializar o mapa:', error);
                    mapElement.style.visibility = 'visible';
                }
            }, 100);
            
        } catch (error) {
            console.error('Erro ao inicializar o mapa:', error);
        }
    }

    /**
     * Configura o marcador no mapa
     */
    function configurarMarcador(lat, lng) {
        // Remove o marcador anterior se existir
        if (marcador) {
            mapa.removeLayer(marcador);
        }
        
        // Adiciona um novo marcador
        marcador = L.marker([lat, lng], {
            draggable: true,
            autoPan: true
        }).addTo(mapa);
        
        // Atualiza as coordenadas quando o marcador é arrastado
        marcador.on('dragend', function() {
            const posicao = marcador.getLatLng();
            atualizarCoordenadas(posicao.lat, posicao.lng);
        });
    }

    /**
     * Atualiza os campos de latitude e longitude
     */
    function atualizarCoordenadas(lat, lng) {
        if (inputLatitude) inputLatitude.value = lat.toFixed(6);
        if (inputLongitude) inputLongitude.value = lng.toFixed(6);
    }

    /**
     * Carrega a lista de eventos
     */
    async function carregarEventos() {
        const loadingRow = document.getElementById('loading-row');
        const mensagemSemDados = document.getElementById('sem-dados');
        
        try {
            // Mostra o indicador de carregamento
            if (loadingRow) loadingRow.classList.remove('d-none');
            if (mensagemSemDados) mensagemSemDados.classList.add('d-none');
            
            console.log('Buscando eventos (todas as páginas)...');

            // Busca paginada da API e agrega todos os resultados para DataTables client-side
            const eventos = [];
            let page = 1;
            const perPage = 100; // traz 100 por página para reduzir requisições
            let totalPages = 1;

            do {
                const url = `/meu-admin/api/eventos/?page=${page}&per_page=${perPage}`;
                const response = await fetch(url);
                if (!response.ok) {
                    const errorText = await response.text();
                    throw new Error(`Erro HTTP ${response.status}: ${errorText}`);
                }
                const data = await response.json();
                if (data && Array.isArray(data.results)) {
                    eventos.push(...data.results);
                } else if (Array.isArray(data)) {
                    eventos.push(...data);
                }
                totalPages = Number(data?.num_pages) || 1;
                page += 1;
            } while (page <= totalPages);

            console.log(`Eventos agregados: ${eventos.length}`);
            
            // Inicializa a tabela com os dados
            inicializarDataTable(eventos);
            
        } catch (error) {
            console.error('Erro ao carregar eventos:', error);
            mostrarAlerta(`Erro ao carregar eventos: ${error.message}`, 'error');
            
            // Mostra mensagem de erro na tabela
            if (mensagemSemDados) {
                mensagemSemDados.textContent = 'Erro ao carregar os eventos';
                mensagemSemDados.classList.remove('d-none');
            }
        } finally {
            // Esconde o indicador de carregamento
            if (loadingRow) loadingRow.classList.add('d-none');
        }
    }
    
    /**
     * Inicializa o DataTables com os dados fornecidos
     */
    function inicializarDataTable(dados) {
        // Destrói a tabela existente se já estiver inicializada
        if ($.fn.DataTable.isDataTable('#tabela-eventos')) {
            $('#tabela-eventos').DataTable().destroy();
            $('#tabela-eventos tbody').empty();
        }

        // Se não houver dados, mostra mensagem
        if (!dados || dados.length === 0) {
            $('#sem-dados').removeClass('d-none');
            $('#loading-row').addClass('d-none');
            return null;
        }

        // Inicializa a tabela
        const table = $('#tabela-eventos').DataTable({
            data: dados,
            columns: [
                { 
                    data: 'titulo',
                    render: function(data) {
                        return data || 'Sem título';
                    }
                },
                { 
                    data: 'local',
                    render: function(data) {
                        return data || '—';
                    }
                },
                { 
                    data: 'palestrante',
                    render: function(data) {
                        return data || '—';
                    }
                },
                { 
                    data: 'start_time',
                    render: function(data) {
                        if (!data) return '—';
                        try {
                            const date = new Date(data);
                            return isNaN(date.getTime()) ? '—' : 
                                `${date.toLocaleDateString()} ${date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}`;
                        } catch (e) {
                            console.error('Erro ao formatar data:', e);
                            return '—';
                        }
                    }
                },
                { 
                    data: 'importante',
                    className: 'text-center',
                    render: function(data) {
                        return data ? 
                            '<span class="badge bg-success">Sim</span>' : 
                            '<span class="badge bg-secondary">Não</span>';
                    }
                },
                {
                    data: 'id',
                    className: 'text-center',
                    orderable: false,
                    render: function(data, type, row) {
                        return `
                            <div class="btn-group btn-group-sm" role="group">
                                <button class="btn btn-outline-primary btn-editar" data-id="${data}">
                                    <i class="fas fa-edit"></i> Editar
                                </button>
                                <button class="btn btn-outline-danger btn-excluir" data-id="${data}">
                                    <i class="fas fa-trash"></i> Excluir
                                </button>
                            </div>
                        `;
                    }
                }
            ],
            language: {
                search: 'Pesquisar:',
                searchPlaceholder: 'Pesquisar eventos...',
                lengthMenu: 'Mostrar _MENU_ itens por página',
                info: 'Mostrando _START_ a _END_ de _TOTAL_ itens',
                infoEmpty: 'Nenhum item encontrado',
                infoFiltered: '(filtrado de _MAX_ itens no total)',
                loadingRecords: 'Carregando...',
                processing: 'Processando...',
                zeroRecords: 'Nenhum registro correspondente encontrado',
                emptyTable: 'Nenhum registro encontrado',
                paginate: {
                    first: 'Primeira',
                    last: 'Última',
                    next: 'Próxima',
                    previous: 'Anterior'
                }
            },
            responsive: true,
            paging: true,
            pagingType: 'simple_numbers',
            pageLength: 10,
            lengthMenu: [10, 25, 50, 100],
            columnDefs: [
                { width: '20%', targets: [0, 2] },
                { width: '15%', targets: [1, 3] },
                { width: '10%', targets: [4, 5] }
            ]
        });
        
        // Configura os eventos da tabela
        configurarEventosTabela();
        
        // Esconde o loading
        const loadingRow = document.getElementById('loading-row');
        if (loadingRow) loadingRow.classList.add('d-none');
        
        return table;
    }
    
    /**
     * Configura os eventos de clique na tabela
     */
    function configurarEventosTabela() {
        // Remove event listeners antigos
        $(document).off('click', '.btn-editar');
        $(document).off('click', '.btn-excluir');
        
        // Adiciona os event listeners com delegação
        $(document).on('click', '.btn-editar', function(e) {
            e.preventDefault();
            const eventoId = $(this).data('id');
            if (eventoId) {
                carregarEventoParaEdicao(eventoId);
            }
        });
        
        $(document).on('click', '.btn-excluir', function(e) {
            e.preventDefault();
            const eventoId = $(this).data('id');
            if (eventoId) {
                confirmarExclusao(eventoId);
            }
        });
    }
    
    /**
     * Manipula o envio do formulário
     */
    async function handleSubmit(e) {
        e.preventDefault();
        
        if (!validarFormulario()) return;
        
        try {
            // Função para formatar data e hora no formato ISO 8601 com fuso horário
            const formatarDataHora = (dataStr, horaStr) => {
                // Cria um objeto Date com a data e hora fornecidas
                const [ano, mes, dia] = dataStr.split('-').map(Number);
                const [hora, minuto] = horaStr.split(':').map(Number);
                const dataHora = new Date(ano, mes - 1, dia, hora, minuto, 0);
                
                // Formata a data no formato ISO 8601
                const pad = num => String(num).padStart(2, '0');
                const tzOffset = -dataHora.getTimezoneOffset();
                const sign = tzOffset >= 0 ? '+' : '-';
                const tzHours = pad(Math.floor(Math.abs(tzOffset) / 60));
                const tzMinutes = pad(Math.abs(tzOffset) % 60);
                
                return `${dataHora.getFullYear()}-${pad(dataHora.getMonth() + 1)}-${pad(dataHora.getDate())}T` +
                       `${pad(dataHora.getHours())}:${pad(dataHora.getMinutes())}:00${sign}${tzHours}:${tzMinutes}`;
            };
            
            const eventoData = {
                titulo: inputTitulo.value.trim(),
                descricao: inputDescricao.value.trim(),
                local: inputLocal.value.trim(),
                palestrante: inputPalestrante?.value.trim() || '',
                start_time: formatarDataHora(inputDataInicio.value, inputHoraInicio.value),
                end_time: formatarDataHora(inputDataFim.value, inputHoraFim.value),
                // Garante que tags seja sempre uma string, mesmo se for um array
                tags: Array.isArray(inputTags?.value) ? inputTags.value[0] : (inputTags?.value.trim() || ''),
                importante: inputImportante.checked,
                ...(inputLatitude?.value && inputLongitude?.value && {
                    latitude: parseFloat(inputLatitude.value),
                    longitude: parseFloat(inputLongitude.value)
                })
            };
            
            console.log('Dados a serem enviados:', JSON.stringify(eventoData, null, 2));

            const url = eventoEditando ? `/meu-admin/api/eventos/${eventoEditando}/` : '/meu-admin/api/eventos/';
            const method = eventoEditando ? 'PUT' : 'POST';

            const response = await fetch(url, {
                method,
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken') || '',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify(eventoData),
                credentials: 'same-origin'
            });

            // Verifica se a resposta está vazia (comum em respostas de sucesso sem corpo)
            const responseText = await response.text();
            let data = {};
            
            try {
                // Tenta fazer o parse apenas se houver conteúdo
                if (responseText) {
                    data = JSON.parse(responseText);
                }
            } catch (error) {
                console.error('Erro ao fazer parse do JSON:', error, 'Resposta:', responseText);
                throw new Error('Resposta inválida do servidor');
            }
            
            if (!response.ok) {
                let errorMessage = 'Ocorreu um erro ao processar sua solicitação';
                
                if (data.detail) {
                    errorMessage = data.detail;
                } else if (data.message) {
                    errorMessage = data.message;
                } else if (data.errors) {
                    // Se houver erros de validação, formata a mensagem
                    const errorMessages = [];
                    for (const [field, errors] of Object.entries(data.errors)) {
                        errorMessages.push(`${field}: ${errors.join(', ')}`);
                    }
                    errorMessage = `Erro de validação: ${errorMessages.join('; ')}`;
                } else if (response.status === 400) {
                    errorMessage = 'Dados inválidos. Verifique as informações fornecidas.';
                } else if (response.status === 403) {
                    errorMessage = 'Você não tem permissão para realizar esta ação';
                } else if (response.status === 404) {
                    errorMessage = 'Recurso não encontrado';
                } else if (response.status === 500) {
                    errorMessage = 'Erro interno do servidor. Tente novamente mais tarde.';
                }
                
                throw new Error(errorMessage);
            }
            
            mostrarAlerta(
                eventoEditando ? 'Evento atualizado com sucesso!' : 'Evento criado com sucesso!', 
                'success'
            );
            
            limparFormulario();
            carregarEventos();
            
        } catch (error) {
            console.error('Erro ao salvar evento:', error);
            mostrarAlerta(
                `Erro ao ${eventoEditando ? 'atualizar' : 'criar'} o evento: ${error.message}`, 
                'error'
            );
        }
    }

    /**
     * Obtém a localização atual do usuário
     */
    function obterLocalizacao() {
        if (!navigator.geolocation) {
            mostrarAlerta('Seu navegador não suporta geolocalização', 'error');
            return;
        }
        
        navigator.geolocation.getCurrentPosition(
            position => {
                const { latitude, longitude } = position.coords;
                atualizarCoordenadas(latitude, longitude);
                
                if (mapa && marcador) {
                    const novaPosicao = L.latLng(latitude, longitude);
                    marcador.setLatLng(novaPosicao);
                    mapa.setView(novaPosicao, 15);
                }
                
                mostrarAlerta('Localização obtida com sucesso!', 'success');
            },
            error => {
                console.error('Erro ao obter localização:', error);
                mostrarAlerta('Não foi possível obter sua localização', 'error');
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 0
            }
        );
    }

    /**
     * Valida o formulário antes do envio
     */
    function validarFormulario() {
        if (!inputTitulo.value.trim()) {
            mostrarAlerta('Por favor, preencha o título do evento', 'error');
            inputTitulo.focus();
            return false;
        }

        if (!inputLocal.value.trim()) {
            mostrarAlerta('Por favor, preencha o local do evento', 'error');
            inputLocal.focus();
            return false;
        }

        if (!inputDataInicio.value || !inputHoraInicio.value || !inputDataFim.value || !inputHoraFim.value) {
            mostrarAlerta('Por favor, preencha todas as datas e horários', 'error');
            return false;
        }

        // Validação de datas
        const dataInicio = new Date(`${inputDataInicio.value}T${inputHoraInicio.value}:00`);
        const dataFim = new Date(`${inputDataFim.value}T${inputHoraFim.value}:00`);
        
        if (dataFim <= dataInicio) {
            mostrarAlerta('A data/hora de término deve ser posterior à data/hora de início', 'error');
            return false;
        }

        return true;
    }
    
    /**
     * Limpa o formulário
     */
    function limparFormulario() {
        if (!formEvento) return;
        
        formEvento.reset();
        eventoEditando = null;
        
        // Limpa campos específicos
        if (inputDescricao) inputDescricao.value = '';
        if (inputPalestrante) inputPalestrante.value = '';
        if (inputTags) inputTags.value = '';
        if (inputImportante) inputImportante.checked = false;
        
        // Reseta o mapa para a posição padrão
        if (mapa) {
            const latPadrao = -1.4558;
            const lngPadrao = -48.5039;
            
            if (marcador) {
                marcador.setLatLng([latPadrao, lngPadrao]);
            }
            
            mapa.setView([latPadrao, lngPadrao], 13);
            
            if (inputLatitude) inputLatitude.value = '';
            if (inputLongitude) inputLongitude.value = '';
        }
        
        // Atualiza o título do formulário
        if (formTitle) {
            formTitle.textContent = 'Adicionar Novo Evento';
        }
        
        // Foca no primeiro campo
        if (inputTitulo) inputTitulo.focus();
    }

    /**
     * Mostra uma mensagem de alerta
     */
    function mostrarAlerta(mensagem, tipo = 'info') {
        // Remove alertas anteriores
        const alertasAnteriores = document.querySelectorAll('.alert-message');
        alertasAnteriores.forEach(alert => alert.remove());
        
        // Cria o elemento de alerta
        const alerta = document.createElement('div');
        alerta.className = `alert alert-${tipo} alert-message`;
        alerta.role = 'alert';
        alerta.innerHTML = `
            ${mensagem}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Fechar"></button>
        `;
        
        // Adiciona o alerta ao topo da página
        const container = document.querySelector('.main-content') || document.body;
        container.insertBefore(alerta, container.firstChild);
        
        // Remove o alerta após 5 segundos
        setTimeout(() => {
            alerta.classList.add('fade-out');
            setTimeout(() => alerta.remove(), 300);
        }, 5000);
    }

    /**
     * Função para confirmar a exclusão de um evento
     */
    window.confirmarExclusao = async function(eventoId) {
        if (!confirm('Tem certeza que deseja excluir este evento?')) {
            return;
        }
        
        try {
            const response = await fetch(`/meu-admin/api/eventos/${eventoId}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken') || '',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Content-Type': 'application/json'
                },
                credentials: 'same-origin'
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Erro ao excluir o evento');
            }
            
            mostrarAlerta('Evento excluído com sucesso!', 'success');
            carregarEventos();
            limparFormulario();
        } catch (error) {
            console.error('Erro ao excluir evento:', error);
            mostrarAlerta(error.message || 'Erro ao excluir o evento', 'error');
        }
    };

    /**
     * Carrega os dados de um evento para edição
     */
    window.carregarEventoParaEdicao = async function(eventoId) {
        try {
            const response = await fetch(`/meu-admin/api/eventos/${eventoId}/`);
            
            if (!response.ok) {
                throw new Error('Erro ao carregar o evento');
            }
            
            // A API pode retornar { success, evento: {...} } ou o objeto do evento diretamente
            const data = await response.json();
            const evento = data && data.evento ? data.evento : data;
            
            // Normaliza campos de data/hora quando o backend envia {data,inicio,fim}
            const startIso = evento.start_time || (evento.data && evento.inicio ? `${evento.data}T${evento.inicio}:00` : null);
            const endIso = evento.end_time || (evento.data && evento.fim ? `${evento.data}T${evento.fim}:00` : null);
            
            // Preenche o formulário com os dados do evento
            if (eventoIdInput) eventoIdInput.value = evento.id;
            if (inputTitulo) inputTitulo.value = evento.titulo || '';
            if (inputDescricao) inputDescricao.value = evento.descricao || '';
            
            // Formata as datas
            if (startIso) {
                const dataInicio = new Date(startIso);
                if (inputDataInicio) inputDataInicio.value = dataInicio.toISOString().split('T')[0];
                if (inputHoraInicio) inputHoraInicio.value = dataInicio.toTimeString().substring(0, 5);
            }
            
            if (endIso) {
                const dataFim = new Date(endIso);
                if (inputDataFim) inputDataFim.value = dataFim.toISOString().split('T')[0];
                if (inputHoraFim) inputHoraFim.value = dataFim.toTimeString().substring(0, 5);
            }
            
            if (inputLocal) inputLocal.value = evento.local || '';
            if (inputPalestrante) inputPalestrante.value = evento.palestrante || '';
            if (inputTags) inputTags.value = Array.isArray(evento.tags) ? evento.tags.join(',') : (evento.tags || evento.tema || '');
            if (inputImportante) inputImportante.checked = evento.importante || false;
            
            // Atualiza o mapa se as coordenadas existirem
            if (evento.latitude && evento.longitude) {
                if (inputLatitude) inputLatitude.value = evento.latitude;
                if (inputLongitude) inputLongitude.value = evento.longitude;
                
                // Atualiza o marcador no mapa
                if (mapa && marcador) {
                    const latLng = L.latLng(evento.latitude, evento.longitude);
                    marcador.setLatLng(latLng);
                    mapa.setView(latLng, 15);
                }
            }
            
            // Rola até o formulário
            document.querySelector('.form-container').scrollIntoView({ behavior: 'smooth' });
            
        } catch (error) {
            console.error('Erro ao carregar evento:', error);
            mostrarAlerta(error.message || 'Erro ao carregar o evento', 'error');
        }
    };

    /**
     * Manipula o envio do formulário (criar/atualizar)
     */
    formEvento.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const eventoId = eventoIdInput ? eventoIdInput.value : null;
        const method = eventoId ? 'PUT' : 'POST';
        const url = eventoId 
            ? `/meu-admin/api/eventos/${eventoId}/`
            : '/meu-admin/api/eventos/';
        
        // Formata as datas para o formato esperado pela API
        const dataInicio = inputDataInicio && inputHoraInicio
            ? `${inputDataInicio.value}T${inputHoraInicio.value}:00`
            : null;
            
        const dataFim = inputDataFim && inputHoraFim
            ? `${inputDataFim.value}T${inputHoraFim.value}:00`
            : null;
        
        // Monta payload, evitando enviar campos opcionais vazios
        const dadosEvento = {
            titulo: inputTitulo ? inputTitulo.value : '',
            start_time: dataInicio,
            end_time: dataFim,
            local: inputLocal ? inputLocal.value : '',
            importante: inputImportante ? inputImportante.checked : false,
        };
        const desc = inputDescricao ? inputDescricao.value : '';
        if (desc !== '') dadosEvento.descricao = desc;
        const pales = inputPalestrante ? inputPalestrante.value : '';
        if (pales !== '') dadosEvento.palestrante = pales;
        const tagsStr = inputTags ? inputTags.value.split(',').map(t => t.trim()).filter(Boolean).join(',') : '';
        if (tagsStr !== '') dadosEvento.tags = tagsStr;
        const lat = inputLatitude ? parseFloat(inputLatitude.value) : NaN;
        const lng = inputLongitude ? parseFloat(inputLongitude.value) : NaN;
        if (Number.isFinite(lat)) dadosEvento.latitude = lat;
        if (Number.isFinite(lng)) dadosEvento.longitude = lng;
        
        try {
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken') || '',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin',
                body: JSON.stringify(dadosEvento)
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                let msg = data && (data.detail || data.message);
                if (!msg && data && data.errors) {
                    const parts = [];
                    for (const [field, errors] of Object.entries(data.errors)) {
                        parts.push(`${field}: ${Array.isArray(errors) ? errors.join(', ') : errors}`);
                    }
                    msg = parts.length ? `Dados inválidos: ${parts.join('; ')}` : 'Dados inválidos';
                }
                throw new Error(msg || 'Erro ao salvar o evento');
            }
            
            mostrarAlerta(
                `Evento ${eventoId ? 'atualizado' : 'criado'} com sucesso!`,
                'success'
            );
            
            // Recarrega a lista e limpa o formulário
            carregarEventos();
            limparFormulario();
            
        } catch (error) {
            console.error('Erro ao salvar evento:', error);
            mostrarAlerta(error.message || 'Erro ao salvar o evento', 'error');
        }
    });

    // Configura o botão de limpar formulário
    if (btnLimpar) {
        btnLimpar.addEventListener('click', limparFormulario);
    }
    
    // Configura o botão de atualizar
    if (btnAtualizar) {
        btnAtualizar.addEventListener('click', carregarEventos);
    }
} // Fecha a função init

// Inicializa a aplicação
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

/**
 * Obtém o valor de um cookie pelo nome
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
 * Função utilitária para debounce
 */
function debounce(func, wait) {
    let timeout;
    return function(...args) {
        const context = this;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), wait);
    };
}

// (init duplicado removido)

// Configuração do DataTable
function initDataTable() {
    if (typeof $ !== 'undefined' && $.fn.DataTable) {
        // Função para renderizar células com truncagem
        const renderWithTooltip = (data, type, row) => {
            if (type === 'display' && data && data.length > 30) {
                return `<span class="text-truncate" style="display: inline-block; max-width: 100%;" title="${data.replace(/"/g, '&quot;')}">${data.substring(0, 30)}...</span>`;
            }
            return data;
        };

        // Destrói a tabela existente se já tiver sido inicializada
        if ($.fn.DataTable.isDataTable('#tabela-eventos')) {
            $('#tabela-eventos').DataTable().destroy();
        }

        // Inicializa a tabela com as configurações
        tabelaEventos = $('#tabela-eventos').DataTable({
            responsive: true,
            language: {
                search: 'Pesquisar:',
                searchPlaceholder: 'Pesquisar eventos...',
                lengthMenu: 'Mostrar _MENU_ itens por página',
                info: 'Mostrando _START_ a _END_ de _TOTAL_ itens',
                infoEmpty: 'Nenhum item encontrado',
                infoFiltered: '(filtrado de _MAX_ itens no total)',
                paginate: {
                    first: 'Primeira',
                    last: 'Última',
                    next: 'Próxima',
                    previous: 'Anterior'
                },
                emptyTable: 'Nenhum registro encontrado',
                zeroRecords: 'Nenhum registro correspondente encontrado'
            },
            order: [[3, 'asc']], // Ordena pela data/hora (coluna 4, índice 3)
            pageLength: 10,
            lengthMenu: [10, 25, 50, 100],
            dom: "<'row'<'col-sm-12 col-md-6'l><'col-sm-12 col-md-6'f>>" +
                 "<'row'<'col-sm-12'tr>>" +
                 "<'row'<'col-sm-12 col-md-5'i><'col-sm-12 col-md-7'p>>",
            processing: true,
            serverSide: false,
            paging: true,
            pagingType: 'simple_numbers',
            retrieve: true,
            destroy: true,
            columns: [
                { 
                    data: 'titulo',
                    render: renderWithTooltip
                },
                { 
                    data: 'local',
                    render: renderWithTooltip
                },
                { 
                    data: 'palestrante',
                    render: renderWithTooltip
                },
                { 
                    data: 'start_time',
                    render: function(data, type, row) {
                        return moment(data).format('DD/MM/YYYY HH:mm');
                    }
                },
                { 
                    data: 'importante',
                    render: function(data) {
                        return data ? '<i class="fas fa-star text-warning"></i>' : '';
                    }
                },
                {
                    data: null,
                    orderable: false,
                    render: function(data, type, row) {
                        return `
                            <div class="btn-group btn-group-sm" role="group">
                                <button type="button" class="btn btn-outline-primary btn-editar" data-id="${row.id}">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button type="button" class="btn btn-outline-danger btn-excluir" data-id="${row.id}">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        `;
                    }
                }
            ],
            columnDefs: [
                { 
                    className: 'text-truncate-cell',
                    targets: [0, 1, 2]
                },
                { 
                    className: 'text-center', 
                    targets: [3, 4, 5]
                }
            ],
            initComplete: function() {
                $('.dataTables_length select').addClass('form-control-sm form-select');
                $('.dataTables_filter input').addClass('form-control-sm');
                
                // Adiciona eventos aos botões de ação
                $('#tabela-eventos').on('click', '.btn-editar', function() {
                    const id = $(this).data('id');
                    carregarEventoParaEdicao(id);
                });
                
                $('#tabela-eventos').on('click', '.btn-excluir', function() {
                    const id = $(this).data('id');
                    confirmarExclusaoEvento(id);
                });
            },
            drawCallback: function() {
                // Atualiza a contagem de itens exibidos
                const api = this.api();
                const total = api.data().count();
                const filtered = api.page.info().recordsDisplay;
                
                if (filtered === 0) {
                    $('.dataTables_info').html('Nenhum registro encontrado');
                } else {
                    const pageInfo = api.page.info();
                    const start = pageInfo.start + 1;
                    const end = Math.min(pageInfo.end, filtered);
                    
                    $('.dataTables_info').html(
                        `Mostrando ${start} a ${end} de ${filtered} itens` +
                        (filtered < total ? ` (filtrado de ${total} itens no total)` : '')
                    );
                }
            }
        });
    }
}

// Adiciona estilos para o fade-out do alerta
const style = document.createElement('style');
style.textContent = `
    .fade-out {
        opacity: 0;
        transition: opacity 0.3s ease-in-out;
    }
    .alert-message {
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 1050;
        max-width: 400px;
        box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
    }
`;
document.head.appendChild(style);
