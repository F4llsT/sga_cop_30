// apps/admin_personalizado/static/admin_personalizado/js/eventos-fixed.js

// Variável global para controlar se o mapa já foi inicializado
let mapaInicializado = false;

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
    function initMapa() {
        // Verifica se o mapa já foi inicializado
        if (mapaInicializado) {
            return;
        }

        // Coordenadas padrão (Belém do Pará)
        const latPadrao = -1.4558;
        const lngPadrao = -48.5039;
        
        // Inicializa o mapa
        try {
            // Verifica se o contêiner do mapa existe
            if (!document.getElementById('map')) {
                console.error('Elemento do mapa não encontrado');
                return;
            }

            // Remove qualquer instância anterior do mapa
            if (mapa) {
                mapa.off();
                mapa.remove();
            }

            // Inicializa o mapa
            mapa = L.map('map', {
                zoomControl: false,  // Vamos adicionar o controle de zoom manualmente
                preferCanvas: true,  // Melhora o desempenho
                tap: false,  // Evita problemas de toque em dispositivos móveis
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
            
            // Configura o marcador
            marcador = L.marker([latPadrao, lngPadrao], {
                draggable: true,
                title: 'Arraste para ajustar a localização',
                autoPan: true
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
                marcador = L.marker([lat, lng], {
                    draggable: true,
                    autoPan: true
                }).addTo(mapa);
                
                // Atualiza os campos de latitude e longitude
                inputLatitude.value = lat.toFixed(6);
                inputLongitude.value = lng.toFixed(6);
                
                // Adiciona o evento de arrastar ao novo marcador
                marcador.on('dragend', function(e) {
                    const posicao = marcador.getLatLng();
                    inputLatitude.value = posicao.lat.toFixed(6);
                    inputLongitude.value = posicao.lng.toFixed(6);
                });
            });
            
            // Força o redesenho do mapa quando a janela for redimensionada
            let resizeTimer;
            window.addEventListener('resize', function() {
                clearTimeout(resizeTimer);
                resizeTimer = setTimeout(function() {
                    if (mapa) {
                        mapa.invalidateSize({animate: true});
                    }
                }, 250);
            });
            
            console.log('Mapa inicializado com sucesso');
            mapaInicializado = true;
            
        } catch (error) {
            console.error('Erro ao inicializar o mapa:', error);
        }
    }

    /**
     * Carrega a lista de palestrantes
     */
    function carregarPalestrantes() {
        // URL correta para a API de palestrantes
        const url = '/api/palestrantes/';
        
        fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken') || ''
            },
            credentials: 'same-origin'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Erro HTTP: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Limpa o select
            inputPalestrantes.innerHTML = '<option value="">Selecione um palestrante</option>';
            
            // Adiciona os palestrantes ao select
            data.forEach(palestrante => {
                const option = document.createElement('option');
                option.value = palestrante.id;
                option.textContent = palestrante.nome;
                inputPalestrantes.appendChild(option);
            });
            
            // Inicializa o Select2
            $(inputPalestrantes).select2({
                theme: 'bootstrap4',
                placeholder: 'Selecione um ou mais palestrantes',
                allowClear: true
            });
        })
        .catch(error => {
            console.error('Erro ao carregar palestrantes:', error);
            mostrarAlerta('Não foi possível carregar a lista de palestrantes', 'error');
        });
    }

    /**
     * Carrega a lista de eventos
     */
    function carregarEventos() {
        // URL correta para a API de eventos
        const url = '/api/eventos/';
        
        fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken') || ''
            },
            credentials: 'same-origin'
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Erro HTTP: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            renderizarEventos(data);
            
            // Inicializa o DataTable
            if ($.fn.DataTable) {
                $('#tabela-eventos').DataTable({
                    language: {
                        url: '//cdn.datatables.net/plug-ins/1.10.25/i18n/Portuguese-Brasil.json'
                    },
                    responsive: true,
                    order: [[1, 'asc']] // Ordena pela data
                });
            }
        })
        .catch(error => {
            console.error('Erro ao carregar eventos:', error);
            mostrarAlerta('Não foi possível carregar a lista de eventos', 'error');
        });
    }

    /**
     * Renderiza a lista de eventos
     */
    function renderizarEventos(eventos) {
        // Implemente a renderização dos eventos aqui
        console.log('Eventos carregados:', eventos);
    }

    /**
     * Configura os eventos do formulário
     */
    function configurarEventos() {
        // Configura o evento de submit do formulário
        formEvento.addEventListener('submit', function(e) {
            e.preventDefault();
            
            if (!validarFormulario()) {
                return false;
            }
            
            const formData = new FormData(formEvento);
            const eventoData = {};
            
            // Converte FormData para objeto
            for (let [key, value] of formData.entries()) {
                eventoData[key] = value;
            }
            
            // Converte para JSON
            const jsonData = JSON.stringify(eventoData);
            
            // URL da API
            const url = eventoEditando ? `/api/eventos/${eventoEditando}/` : '/api/eventos/';
            const method = eventoEditando ? 'PUT' : 'POST';
            
            fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken') || '',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: jsonData,
                credentials: 'same-origin'
            })
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => { throw err; });
                }
                return response.json();
            })
            .then(data => {
                mostrarAlerta('Evento salvo com sucesso!', 'success');
                limparFormulario();
                carregarEventos();
            })
            .catch(error => {
                console.error('Erro ao salvar evento:', error);
                const mensagem = error.detail || 'Não foi possível salvar o evento';
                mostrarAlerta(mensagem, 'error');
            });
        });
        
        // Configura o botão de limpar
        if (btnLimpar) {
            btnLimpar.addEventListener('click', limparFormulario);
        }
        
        // Configura o botão de localização
        if (btnLocalizar) {
            btnLocalizar.addEventListener('click', function() {
                if (navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(
                        function(position) {
                            const lat = position.coords.latitude;
                            const lng = position.coords.longitude;
                            
                            // Atualiza os campos de latitude e longitude
                            inputLatitude.value = lat.toFixed(6);
                            inputLongitude.value = lng.toFixed(6);
                            
                            // Atualiza o marcador no mapa
                            if (mapa && marcador) {
                                const novaPosicao = L.latLng(lat, lng);
                                marcador.setLatLng(novaPosicao);
                                mapa.setView(novaPosicao, 15);
                            }
                            
                            mostrarAlerta('Localização obtida com sucesso!', 'success');
                        },
                        function(error) {
                            console.error('Erro ao obter localização:', error);
                            mostrarAlerta('Não foi possível obter sua localização', 'error');
                        },
                        {
                            enableHighAccuracy: true,
                            timeout: 10000,
                            maximumAge: 0
                        }
                    );
                } else {
                    mostrarAlerta('Seu navegador não suporta geolocalização', 'error');
                }
            });
        }
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
        
        if (!inputDataInicio.value) {
            mostrarAlerta('Por favor, selecione a data de início', 'error');
            inputDataInicio.focus();
            return false;
        }
        
        if (!inputHoraInicio.value) {
            mostrarAlerta('Por favor, selecione o horário de início', 'error');
            inputHoraInicio.focus();
            return false;
        }
        
        if (!inputLocal.value.trim()) {
            mostrarAlerta('Por favor, informe o local do evento', 'error');
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
        
        // Limpa os campos específicos
        if (inputPalestrantes && inputPalestrantes.select2) {
            $(inputPalestrantes).val(null).trigger('change');
        }
        
        // Reseta o título do formulário
        if (formTitle) {
            formTitle.textContent = 'Adicionar Novo Evento';
        }
        
        // Reseta o botão de submit
        const btnSubmit = formEvento.querySelector('button[type="submit"]');
        if (btnSubmit) {
            btnSubmit.innerHTML = '<i class="fas fa-save"></i> Salvar Evento';
        }
        
        // Reseta o mapa para a posição inicial
        if (mapa) {
            const latPadrao = -1.4558;
            const lngPadrao = -48.5039;
            
            // Remove o marcador existente
            if (marcador) {
                mapa.removeLayer(marcador);
            }
            
            // Adiciona um novo marcador na posição padrão
            marcador = L.marker([latPadrao, lngPadrao], {
                draggable: true,
                autoPan: true
            }).addTo(mapa);
            
            // Centraliza o mapa na posição padrão
            mapa.setView([latPadrao, lngPadrao], 13);
            
            // Atualiza os campos de latitude e longitude
            inputLatitude.value = latPadrao.toFixed(6);
            inputLongitude.value = lngPadrao.toFixed(6);
            
            // Adiciona o evento de arrastar ao novo marcador
            marcador.on('dragend', function(e) {
                const posicao = marcador.getLatLng();
                inputLatitude.value = posicao.lat.toFixed(6);
                inputLongitude.value = posicao.lng.toFixed(6);
            });
        }
    }

    /**
     * Mostra uma mensagem de alerta
     */
    function mostrarAlerta(mensagem, tipo = 'info') {
        // Remove alertas anteriores
        const alertasAnteriores = document.querySelectorAll('.alert-dismissible');
        alertasAnteriores.forEach(alerta => alerta.remove());
        
        // Cria o elemento do alerta
        const alerta = document.createElement('div');
        alerta.className = `alert alert-${tipo} alert-dismissible fade show`;
        alerta.role = 'alert';
        
        // Adiciona o ícone de acordo com o tipo
        let icone = '';
        switch(tipo) {
            case 'success':
                icone = 'check-circle';
                break;
            case 'danger':
            case 'error':
                icone = 'exclamation-triangle';
                tipo = 'danger'; // Padroniza para 'danger' que é a classe do Bootstrap
                break;
            case 'warning':
                icone = 'exclamation-circle';
                break;
            default:
                icone = 'info-circle';
        }
        
        alerta.innerHTML = `
            <i class="fas fa-${icone} me-2"></i>
            ${mensagem}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Fechar"></button>
        `;
        
        // Adiciona o alerta ao início do conteúdo principal
        const mainContent = document.querySelector('.main-content');
        if (mainContent) {
            mainContent.insertBefore(alerta, mainContent.firstChild);
            
            // Remove o alerta após 5 segundos
            setTimeout(() => {
                if (alerta && alerta.parentNode) {
                    alerta.remove();
                }
            }, 5000);
        }
    }

    /**
     * Obtém o valor de um cookie
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
});
