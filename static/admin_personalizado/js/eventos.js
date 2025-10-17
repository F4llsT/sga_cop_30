/**
 * eventos-new.js
 * Script para gerenciamento de eventos no painel administrativo
 * Versão: 1.0.0
 */

// Variável global para controle de estado do mapa
let mapaInicializado = false;

// Inicialização quando o DOM estiver pronto
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

    // Inicialização
    initMapa();
    carregarEventos();
    configurarEventos();

    /**
     * Inicializa o mapa usando Leaflet
     */
    function initMapa() {
        if (mapaInicializado) return;

        // Coordenadas padrão (Belém do Pará)
        const latPadrao = -1.4558;
        const lngPadrao = -48.5039;
        
        try {
            if (!document.getElementById('map')) {
                console.error('Elemento do mapa não encontrado');
                return;
            }

            // Remove instância anterior do mapa, se existir
            if (mapa) {
                mapa.off();
                mapa.remove();
            }

            // Inicializa o mapa com configurações otimizadas
            mapa = L.map('map', {
                zoomControl: false,
                preferCanvas: true,
                tap: false,
                zoomSnap: 0.1,
                zoomDelta: 0.1,
                wheelPxPerZoomLevel: 60
            }).setView([latPadrao, lngPadrao], 13);
            
            // Adiciona o tile layer (OpenStreetMap)
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors',
                maxZoom: 19,
                minZoom: 2,
                noWrap: true,
                updateWhenIdle: true
            }).addTo(mapa);
            
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
            window.addEventListener('resize', debounce(() => {
                if (mapa) mapa.invalidateSize({animate: true});
            }, 250));
            
            mapaInicializado = true;
            console.log('Mapa inicializado com sucesso');
            
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
        const tabelaEventos = document.getElementById('tabela-eventos');
        const loadingRow = document.getElementById('loading-row');
        const mensagemSemDados = document.getElementById('sem-dados');
        
        if (!tabelaEventos || !loadingRow) return;
        
        try {
            loadingRow.classList.remove('d-none');
            if (mensagemSemDados) mensagemSemDados.classList.add('d-none');
            
            const response = await fetch('/meu-admin/api/eventos/');
            if (!response.ok) {
                throw new Error(`Erro HTTP: ${response.status}`);
            }
            
            const eventos = await response.json();
            const tbody = tabelaEventos.querySelector('tbody');
            
            if (!tbody) return;
            
            tbody.innerHTML = '';
            
            if (eventos.length === 0) {
                if (mensagemSemDados) mensagemSemDados.classList.remove('d-none');
                return;
            }
            
            // Adiciona cada evento à tabela
            eventos.forEach(evento => {
                const tr = document.createElement('tr');
                const dataInicio = evento.start_time ? new Date(evento.start_time) : null;
                const dataFormatada = dataInicio ? 
                    `${dataInicio.toLocaleDateString()} ${dataInicio.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}` : 
                    'Não definido';
                
                tr.innerHTML = `
                    <td>${evento.titulo || 'Sem título'}</td>
                    <td>${evento.local || '—'}</td>
                    <td>${evento.palestrante || '—'}</td>
                    <td>${dataFormatada}</td>
                    <td>${evento.importante ? 'Sim' : 'Não'}</td>
                    <td class="text-center">
                        <div class="btn-group btn-group-sm" role="group">
                            <a href="/meu-admin/eventos/${evento.id}/editar/" class="btn btn-outline-primary">
                                <i class="fas fa-edit"></i> Editar
                            </a>
                            <button type="button" class="btn btn-outline-danger" onclick="confirmarExclusao(${evento.id})">
                                <i class="fas fa-trash"></i> Excluir
                            </button>
                        </div>
                    </td>
                `;
                
                tbody.appendChild(tr);
            });
            
        } catch (error) {
            console.error('Erro ao carregar eventos:', error);
            mostrarAlerta(`Erro ao carregar eventos: ${error.message}`, 'error');
        } finally {
            loadingRow.classList.add('d-none');
        }
    }

    /**
     * Configura os eventos do formulário
     */
    function configurarEventos() {
        // Evento de submit do formulário
        formEvento?.addEventListener('submit', handleSubmit);
        
        // Botão de limpar
        btnLimpar?.addEventListener('click', limparFormulario);
        
        // Botão de localização
        btnLocalizar?.addEventListener('click', obterLocalizacao);
        
        // Botão de atualizar
        btnAtualizar?.addEventListener('click', carregarEventos);
        
        // Busca em tempo real
        searchInput?.addEventListener('input', debounce(carregarEventos, 300));
    }
    
    /**
     * Manipula o envio do formulário
     */
    async function handleSubmit(e) {
        e.preventDefault();
        
        if (!validarFormulario()) return;
        
        try {
            const eventoData = {
                titulo: inputTitulo.value.trim(),
                descricao: inputDescricao.value.trim(),
                local: inputLocal.value.trim(),
                palestrante: inputPalestrante?.value.trim() || '',
                start_time: `${inputDataInicio.value}T${inputHoraInicio.value}:00`,
                end_time: `${inputDataFim.value}T${inputHoraFim.value}:00`,
                tags: inputTags?.value.trim() || '',
                importante: inputImportante.checked,
                ...(inputLatitude?.value && inputLongitude?.value && {
                    latitude: parseFloat(inputLatitude.value),
                    longitude: parseFloat(inputLongitude.value)
                })
            };

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
                throw new Error(data.detail || data.message || `Erro ${response.status}: ${response.statusText}`);
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
        const camposObrigatorios = [
            { campo: inputTitulo, mensagem: 'Por favor, preencha o título do evento' },
            { campo: inputDataInicio, mensagem: 'Por favor, selecione a data de início' },
            { campo: inputHoraInicio, mensagem: 'Por favor, selecione o horário de início' },
            { campo: inputLocal, mensagem: 'Por favor, informe o local do evento' }
        ];

        for (const { campo, mensagem } of camposObrigatorios) {
            if (!campo?.value?.trim()) {
                mostrarAlerta(mensagem, 'error');
                campo.focus();
                return false;
            }
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
    window.confirmarExclusao = function(eventoId) {
        if (!confirm('Tem certeza que deseja excluir este evento?')) {
            return;
        }
        
        fetch(`/api/eventos/${eventoId}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken') || '',
                'X-Requested-With': 'XMLHttpRequest'
            },
            credentials: 'same-origin'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro ao excluir o evento');
            }
            mostrarAlerta('Evento excluído com sucesso!', 'success');
            carregarEventos();
        })
        .catch(error => {
            console.error('Erro ao excluir evento:', error);
            mostrarAlerta('Erro ao excluir o evento', 'error');
        });
    };
});

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

/**
 * Função para inicializar o DataTables
 */
function initDataTable() {
    if (typeof $ !== 'undefined' && $.fn.DataTable) {
        $('#tabela-eventos').DataTable({
            language: {
                url: 'https://cdn.datatables.net/plug-ins/1.11.5/i18n/pt-BR.json'
            },
            responsive: true,
            order: [[3, 'asc']], // Ordena pela coluna de data
            columnDefs: [
                { orderable: false, targets: [5] } // Desabilita ordenação na coluna de ações
            ]
        });
    }
}

// Inicializa o DataTables quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    // Inicializa o DataTables
    initDataTable();
    
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
});
