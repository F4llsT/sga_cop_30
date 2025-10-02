/**
 * Passe Fácil - Painel de Administração
 * Script principal para funcionalidades do painel
 */
// No início do seu arquivo passefacilADM.js, adicione:
document.addEventListener('DOMContentLoaded', function() {
    console.log('=== INICIALIZAÇÃO DO SISTEMA ===');
    console.log('Versão do Chart.js:', Chart ? Chart.version : 'Chart.js não carregado');
    console.log('Elementos encontrados:', {
        passesTableBody: document.getElementById('passesTableBody'),
        searchInput: document.getElementById('searchInput'),
        totalResults: document.getElementById('totalResults'),
        validationsList: document.getElementById('validationsList')
    });

    
    // Inicializa a aplicação
    function init() {
        console.log('Iniciando aplicação...');
        console.log('Elementos encontrados:', {
            listView: document.getElementById('listView'),
            validateView: document.getElementById('validateView'),
            listViewBtn: document.getElementById('listViewBtn'),
            validateViewBtn: document.getElementById('validateViewBtn')
        });
        
        setupEventListeners();
        // Inicializa o gráfico somente agora (elements já inicializado)
        if (window.chartData) {
            initChart();
        } else {
            console.warn('Dados do gráfico não encontrados');
        }
        showView('list');
        updateDateTime();
        
        // Atualiza a data a cada minuto
        setInterval(updateDateTime, 60000);
        
        // Atualiza os resultados da busca inicial
        updateSearchResults();
    }
    
    // Atualiza os resultados da busca
    function updateSearchResults() {
        if (!elements.searchInput) return;
        
        // Dispara o evento de input para aplicar a busca atual
        const event = new Event('input', {
            bubbles: true,
            cancelable: true,
        });
        elements.searchInput.dispatchEvent(event);
    }

    // Atualiza a cada minuto
    setInterval(updateSearchResults, 60000);

    // Elementos da interface
    const elements = {
        // Views
        listView: document.getElementById('listView'),
        validateView: document.getElementById('validateView'),
        
        // Botões de navegação
        listViewBtn: document.getElementById('listViewBtn'),
        validateViewBtn: document.getElementById('validateViewBtn'),
        
        // Elementos da lista
        searchInput: document.getElementById('searchInput'),
        passesTableBody: document.getElementById('passesTableBody'),
        totalResults: document.getElementById('totalResults'),
        
        // Elementos de validação
        qrTab: document.getElementById('qrTab'),
        manualTab: document.getElementById('manualTab'),
        tabButtons: document.querySelectorAll('.tab-btn'),
        toggleCameraBtn: document.getElementById('toggleCameraBtn'),
        cameraFeed: document.getElementById('cameraFeed'),
        manualCodeInput: document.getElementById('manualCodeInput'),
        validateManualBtn: document.getElementById('validateManualBtn'),
        
        // Elementos do gráfico
        miniChart: document.getElementById('miniChart'),
        
        // Histórico de validações
        validationsList: document.getElementById('validationsList'),
        recentValidationsCount: document.getElementById('recentValidationsCount'),
        
        // Modal
        modal: document.getElementById('validationModal'),
        closeModal: document.getElementById('closeModal'),
        closeModalBtn: document.getElementById('closeModalBtn'),
        newValidationBtn: document.getElementById('newValidationBtn'),
        modalTitle: document.getElementById('modalTitle'),
        validationResult: document.getElementById('validationResult'),
        modalUser: document.getElementById('modalUser'),
        modalCode: document.getElementById('modalCode'),
        modalDateTime: document.getElementById('modalDateTime')
    };

    // Estado da aplicação
    let state = {
        currentView: 'list',
        currentTab: 'qrTab',
        isCameraActive: false,
        mediaStream: null
    };
    
    // Inicialização do gráfico
    function initChart() {
        if (!window.chartData) return;
        
        const ctx = document.createElement('canvas');
        elements.miniChart.appendChild(ctx);
        
        new Chart(ctx, {
            type: 'line',
            data: window.chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        displayColors: false,
                        callbacks: {
                            label: function(context) {
                                return `${context.dataset.label}: ${context.raw}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        display: true,
                        grid: {
                            display: false
                        },
                        ticks: {
                            maxRotation: 0,
                            padding: 5
                        }
                    },
                    y: {
                        display: false,
                        beginAtZero: true
                    }
                },
                elements: {
                    point: {
                        radius: 0
                    },
                    line: {
                        borderWidth: 2,
                        tension: 0.3
                    }
                }
            }
        });
    }
    
    // Inicializa o clipboard para o botão de copiar
    function initClipboard() {
        const copyButtons = document.querySelectorAll('.copy-btn');
        
        copyButtons.forEach(button => {
            button.addEventListener('click', function() {
                const code = this.getAttribute('data-clipboard-text');
                navigator.clipboard.writeText(code).then(() => {
                    // Feedback visual
                    const originalHTML = this.innerHTML;
                    this.innerHTML = '<i class="icon-check"></i>';
                    this.classList.add('copied');
                    
                    setTimeout(() => {
                        this.innerHTML = originalHTML;
                        this.classList.remove('copied');
                    }, 2000);
                });
            });
        });
    }
    // Configura a busca
    function setupSearch() {
        elements.searchInput.addEventListener('input', handleSearch);
    }
    
    // Manipula a busca
    function handleSearch(e) {
        console.log('Buscando por:', e.target.value);
        
        if (!elements.passesTableBody || !elements.totalResults) {
            console.warn('Elementos necessários não encontrados');
            return;
        }
        
        const searchTerm = e.target.value.toLowerCase().trim();
        const rows = elements.passesTableBody.querySelectorAll('tr');
        let visibleCount = 0;
        
        // Remove mensagens de "Nenhum resultado" anteriores
        const existingNoResults = elements.passesTableBody.querySelector('.no-results');
        if (existingNoResults) {
            existingNoResults.remove();
        }
        
        rows.forEach(row => {
            // Pula linhas vazias ou de mensagem
            if (row.classList.contains('empty-row') || row.classList.contains('no-results')) {
                row.style.display = 'none';
                return;
            }
            
            const text = row.textContent.toLowerCase();
            const isVisible = searchTerm === '' || text.includes(searchTerm);
            row.style.display = isVisible ? '' : 'none';
            
            if (isVisible) visibleCount++;
        });
        
        // Atualiza a contagem de resultados
        elements.totalResults.textContent = visibleCount;
        
        // Mostra mensagem se não houver resultados
        if (visibleCount === 0 && searchTerm !== '') {
            const noResultsRow = document.createElement('tr');
            noResultsRow.className = 'no-results';
            noResultsRow.innerHTML = '<td colspan="3" class="text-center">Nenhum resultado encontrado para "' + searchTerm + '"</td>';
            elements.passesTableBody.appendChild(noResultsRow);
        }
        
        console.log('Busca concluída. Resultados encontrados:', visibleCount);
    }
    
    // Configura os event listeners
    function setupEventListeners() {
        console.log('Configurando event listeners...');
        
        // Verifica se os botões existem
        console.log('Botões:', {
            listViewBtn: elements.listViewBtn,
            validateViewBtn: elements.validateViewBtn
        });
        // Navegação entre views
        if (elements.listViewBtn) {
            elements.listViewBtn.addEventListener('click', () => showView('list'));
        }
        
        if (elements.validateViewBtn) {
            elements.validateViewBtn.addEventListener('click', () => showView('validate'));
        }
        
        // Navegação entre abas
        if (elements.tabButtons) {
            elements.tabButtons.forEach(btn => {
                btn.addEventListener('click', () => {
                    const tabId = btn.getAttribute('data-tab');
                    showTab(tabId);
                });
            });
        }
        
        // Validação manual
        if (elements.manualCodeInput) {
            elements.manualCodeInput.addEventListener('input', toggleValidateButton);
            elements.manualCodeInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && elements.validateManualBtn && !elements.validateManualBtn.disabled) {
                    validateManualCode();
                }
            });
        }
        
        if (elements.validateManualBtn) {
            elements.validateManualBtn.addEventListener('click', validateManualCode);
        }
        
        // Câmera QR Code
        if (elements.toggleCameraBtn) {
            elements.toggleCameraBtn.addEventListener('click', toggleCamera);
        }
        
        // Modal
        if (elements.closeModal) {
            elements.closeModal.addEventListener('click', closeModal);
        }
        
        if (elements.closeModalBtn) {
            elements.closeModalBtn.addEventListener('click', closeModal);
        }
        
        if (elements.newValidationBtn) {
            elements.newValidationBtn.addEventListener('click', () => {
                closeModal();
                showView('validate');
            });
        }
        
        // Fecha o modal ao clicar fora do conteúdo
        window.addEventListener('click', (e) => {
            if (e.target === elements.modal) {
                closeModal();
            }
        });
        
        // Busca na lista
        if (elements.searchInput) {
            elements.searchInput.addEventListener('input', handleSearch);
        }
        
        // Simular leitura de QR Code (apenas para demonstração)
        if (elements.cameraFeed) {
            elements.cameraFeed.addEventListener('click', simulateQRCodeScan);
        }
    }

    // Atualiza a data e hora no cabeçalho
    function updateDateTime() {
        const now = new Date();
        const dateTimeElement = document.getElementById('currentDateTime');
        const timeElement = document.getElementById('current-time');
        const dateElement = document.getElementById('current-date');
        
        // Atualiza o elemento combinado (data e hora)
        if (dateTimeElement) {
            const options = { 
                weekday: 'long', 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            };
            dateTimeElement.textContent = now.toLocaleDateString('pt-BR', options);
        }
        
        // Atualiza elementos separados (se existirem)
        if (timeElement) {
            const timeString = now.toLocaleTimeString('pt-BR', { 
                hour: '2-digit', 
                minute: '2-digit', 
                second: '2-digit' 
            });
            timeElement.textContent = timeString;
        }
        
        if (dateElement) {
            const dateString = now.toLocaleDateString('pt-BR', { 
                day: '2-digit', 
                month: '2-digit', 
                year: 'numeric' 
            });
            dateElement.textContent = dateString;
        }
    }

    // Alterna entre as views (lista/validação)
    function showView(viewName) {
        console.log('showView chamado com:', viewName);
        console.log('Elementos:', {
            listView: elements.listView,
            validateView: elements.validateView,
            listViewBtn: elements.listViewBtn,
            validateViewBtn: elements.validateViewBtn
        });
        
        state.currentView = viewName;
        
        // Atualiza a UI
        if (elements.listView) elements.listView.classList.toggle('active', viewName === 'list');
        if (elements.validateView) elements.validateView.classList.toggle('active', viewName === 'validate');
        
        // Atualiza os botões de navegação
        if (elements.listViewBtn) elements.listViewBtn.classList.toggle('active', viewName === 'list');
        if (elements.validateViewBtn) elements.validateViewBtn.classList.toggle('active', viewName === 'validate');
        
        // Se estiver saindo da view de validação, desativa a câmera
        if (viewName !== 'validate' && state.isCameraActive) {
            toggleCamera();
        }
        
        // Se estiver entrando na view de validação, mostra a aba ativa
        if (viewName === 'validate' && elements.validateView) {
            showTab(state.currentTab);
        }
    }

    // Alterna entre as abas (QR Code / Código Manual)
    function showTab(tabId) {
        // Atualiza o estado
        state.currentTab = tabId;
        
        // Esconde todos os painéis
        document.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.remove('active');
        });
        
        // Remove a classe ativa de todos os botões
        elements.tabButtons.forEach(btn => {
            btn.classList.remove('active');
        });
        
        // Ativa o painel e o botão correspondentes
        const activePane = document.getElementById(tabId);
        const activeButton = document.querySelector(`[data-tab="${tabId}"]`);
        
        if (activePane) activePane.classList.add('active');
        if (activeButton) activeButton.classList.add('active');
        
        // Se for a aba da câmera e a câmera já estiver ativa, garante que está visível
        if (tabId === 'qrTab' && state.isCameraActive) {
            initCamera();
        } else if (tabId !== 'qrTab' && state.isCameraActive) {
            // Se estiver saindo da aba da câmera, desativa a câmera
            toggleCamera();
        }
    }

    // (removido) Versão alternativa de handleSearch evitada para manter consistência com elements.passesTableBody

    // Renderiza a lista de passes
   // Renderiza a lista de passes
function renderPassesList() {
    console.log('Atualizando lista de passes...');
    
    if (!elements.passesTableBody) {
        console.warn('Elemento passesTableBody não encontrado');
        return;
    }
    
    const searchTerm = elements.searchInput ? elements.searchInput.value.toLowerCase().trim() : '';
    const rows = elements.passesTableBody.querySelectorAll('tr');
    let visibleCount = 0;
    
    // Remove mensagens de "Nenhum resultado" anteriores
    const existingNoResults = elements.passesTableBody.querySelector('.no-results, .empty-row');
    if (existingNoResults) {
        existingNoResults.remove();
    }
    
    // Se não houver linhas, não há nada para fazer
    if (rows.length === 0) {
        console.log('Nenhuma linha encontrada na tabela');
        return;
    }
    
    // Conta as linhas visíveis
    rows.forEach(row => {
        // Pula linhas vazias ou de mensagem
        if (row.classList.contains('empty-row') || row.classList.contains('no-results')) {
            row.style.display = 'none';
            return;
        }
        
        const text = row.textContent.toLowerCase();
        const isVisible = searchTerm === '' || text.includes(searchTerm);
        row.style.display = isVisible ? '' : 'none';
        
        if (isVisible) visibleCount++;
    });
    
    // Atualiza a contagem de resultados
    if (elements.totalResults) {
        elements.totalResults.textContent = visibleCount;
    }
    
    // Mostra mensagem se não houver resultados
    if (visibleCount === 0 && searchTerm !== '') {
        const noResultsRow = document.createElement('tr');
        noResultsRow.className = 'no-results';
        noResultsRow.innerHTML = '<td colspan="4" class="text-center">Nenhum resultado encontrado para "' + searchTerm + '"</td>';
        elements.passesTableBody.appendChild(noResultsRow);
    }
    
    console.log('Lista de passes atualizada. Resultados encontrados:', visibleCount);
}

    // Renderiza a lista de validações recentes
    function renderValidationsList() {
        // A renderização é feita pelo Django template
        // Esta função é mantida para compatibilidade
        if (!elements.validationsList) return;
        
        // Apenas atualiza a contagem se houver validações
        const validationItems = elements.validationsList.querySelectorAll('.validation-item');
        if (validationItems.length === 0) {
            const emptyState = elements.validationsList.querySelector('.empty-state');
            if (!emptyState) {
                elements.validationsList.innerHTML = `
                    <div class="empty-state">
                        <i class="icon-clock"></i>
                        <p>Nenhuma validação recente</p>
                    </div>
                `;
            }
        } else if (elements.recentValidationsCount) {
            elements.recentValidationsCount.textContent = validationItems.length;
        }
    }

    // Atualiza o contador de validações recentes
    function updateValidationsCount() {
        // O contador é atualizado pelo Django template
        // Esta função é mantida para compatibilidade
        if (!elements.recentValidationsCount) return;
        
        const validationItems = elements.validationsList?.querySelectorAll('.validation-item') || [];
        elements.recentValidationsCount.textContent = validationItems.length;
    }

    // Alterna o estado da câmera (ligar/desligar)
    async function toggleCamera() {
        if (state.isCameraActive) {
            // Desativa a câmera
            if (state.mediaStream) {
                state.mediaStream.getTracks().forEach(track => track.stop());
                state.mediaStream = null;
            }
            
            elements.cameraFeed.innerHTML = `
                <div class="scanner-frame">
                    <div class="scanner-corner top-left"></div>
                    <div class="scanner-corner top-right"></div>
                    <div class="scanner-corner bottom-left"></div>
                    <div class="scanner-corner bottom-right"></div>
                </div>
                <p class="camera-hint">Posicione o QR Code dentro da área destacada</p>
            `;
            
            elements.toggleCameraBtn.innerHTML = `
                <i class="icon-camera"></i>
                <span>Iniciar Câmera</span>
            `;
            
            state.isCameraActive = false;
        } else {
            // Ativa a câmera
            try {
                await initCamera();
                elements.toggleCameraBtn.innerHTML = `
                    <i class="material-icons">stop</i>
                    <span>Parar Câmera</span>
                `;
                state.isCameraActive = true;
            } catch (error) {
                console.error('Erro ao acessar a câmera:', error);
                alert('Não foi possível acessar a câmera. Verifique as permissões e tente novamente.');
            }
        }
    }

    // Inicializa a câmera
    async function initCamera() {
        if (state.mediaStream) {
            // Já está inicializada
            return;
        }
        
        try {
            // Tenta acessar a câmera traseira (environment) primeiro
            const constraints = {
                video: {
                    facingMode: 'environment',
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                }
            };
            
            state.mediaStream = await navigator.mediaDevices.getUserMedia(constraints);
            
            // Cria o elemento de vídeo se não existir
            let videoElement = elements.cameraFeed.querySelector('video');
            if (!videoElement) {
                videoElement = document.createElement('video');
                videoElement.autoplay = true;
                videoElement.playsInline = true;
                elements.cameraFeed.innerHTML = '';
                elements.cameraFeed.appendChild(videoElement);
                
                // Adiciona o frame do scanner por cima do vídeo
                const scannerFrame = document.createElement('div');
                scannerFrame.className = 'scanner-frame';
                scannerFrame.innerHTML = `
                    <div class="scanner-corner top-left"></div>
                    <div class="scanner-corner top-right"></div>
                    <div class="scanner-corner bottom-left"></div>
                    <div class="scanner-corner bottom-right"></div>
                `;
                elements.cameraFeed.appendChild(scannerFrame);
                
                const hint = document.createElement('p');
                hint.className = 'camera-hint';
                hint.textContent = 'Posicione o QR Code dentro da área destacada';
                elements.cameraFeed.appendChild(hint);
            }
            
            videoElement.srcObject = state.mediaStream;
            
            // Aqui você pode adicionar a lógica de leitura de QR Code
            // Por exemplo, usando uma biblioteca como jsQR
            
        } catch (error) {
            console.error('Erro ao acessar a câmera:', error);
            throw error;
        }
    }

    // Simula a leitura de um QR Code (apenas para demonstração)
    function simulateQRCodeScan() {
        if (!state.isCameraActive) return;
        
        // Mostra um prompt para o usuário inserir um código
        const code = prompt('Digite o código do passe para simular a leitura:');
        if (code) {
            validateCode(code);
        }
    }

    // Habilita/desabilita o botão de validar com base no input
    function toggleValidateButton() {
        if (elements.validateManualBtn) {
            elements.validateManualBtn.disabled = elements.manualCodeInput.value.trim() === '';
        }
    }

    // Valida um código manualmente
    function validateManualCode() {
        const code = elements.manualCodeInput.value.trim();
        if (code) {
            validateCode(code);
            elements.manualCodeInput.value = '';
            elements.validateManualBtn.disabled = true;
        }
    }

    function validateCode(code) {
        if (!code) {
            console.error('Nenhum código fornecido para validação');
            return;
        }
        
        showLoading(true);
        
        const url = `/passefacil/api/validar-qr-code/?codigo=${encodeURIComponent(code)}`;
        console.log('=== VALIDAÇÃO DE CÓDIGO ===');
        console.log('Código a ser validado:', code);
        console.log('URL da requisição:', url);
        
        fetch(url, {
            headers: {
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCookie('csrftoken') || ''
            },
            credentials: 'same-origin',
            cache: 'no-store' // Evita cache para garantir requisições sempre atualizadas
        })
        .then(async response => {
            const contentType = response.headers.get('content-type') || '';
            const isJson = contentType.includes('application/json');
            const text = await response.text();
            
            console.log('=== RESPOSTA DO SERVIDOR ===');
            console.log('Status:', response.status, response.statusText);
            console.log('Content-Type:', contentType);
            console.log('Resposta bruta:', text);
            
            if (!response.ok) {
                const error = new Error(`Erro HTTP! status: ${response.status} ${response.statusText}`);
                error.response = { status: response.status, statusText: response.statusText };
                throw error;
            }
            
            if (!isJson) {
                console.warn('A resposta não é um JSON válido. Content-Type:', contentType);
                try {
                    // Tenta fazer parse mesmo assim, caso o content-type esteja incorreto
                    const data = JSON.parse(text);
                    return data;
                } catch (e) {
                    console.error('Falha ao fazer parse do JSON:', e);
                    throw new Error('Resposta do servidor não é um JSON válido');
                }
            }
            
            return JSON.parse(text);
        })
        .then(data => {
            if (!data) {
                throw new Error('Nenhum dado retornado pelo servidor');
            }
            
            console.log('Dados da resposta:', JSON.stringify(data, null, 2));
            
            const now = new Date();
            const timeString = now.toLocaleTimeString('pt-BR', { 
                hour: '2-digit', 
                minute: '2-digit', 
                second: '2-digit' 
            });
            
            if (data.valido) {
                console.log('Validação bem-sucedida para o código:', truncateCode(code));
                showValidationResult(
                    true,
                    (data.usuario && (data.usuario.nome || data.usuario.email)) || 'Usuário',
                    truncateCode(code),
                    timeString,
                    data.mensagem || 'Validação bem-sucedida'
                );
                
                // Atualiza a tabela localmente
                updateLocalUI(code, data, now, timeString);
            } else {
                console.warn('Validação falhou para o código:', truncateCode(code), 'Motivo:', data.mensagem || 'Não especificado');
                showValidationResult(
                    false,
                    (data.usuario && (data.usuario.nome || data.usuario.email)) || 'Código inválido',
                    truncateCode(code),
                    timeString,
                    data.mensagem || 'Não foi possível validar o código'
                );
            }
        })
        .catch(error => {
            console.error('=== ERRO NA VALIDAÇÃO ===');
            console.error('Mensagem:', error.message);
            console.error('Stack:', error.stack);
            if (error.response) {
                console.error('Detalhes da resposta:', error.response);
            }
            
            const timeString = new Date().toLocaleTimeString('pt-BR', { 
                hour: '2-digit', 
                minute: '2-digit', 
                second: '2-digit' 
            });
            
            let errorMessage = `Erro: ${error.message || 'Erro desconhecido'}`;
            if (error.response) {
                errorMessage += ` (Status: ${error.response.status})`;
            }
            
            showValidationResult(
                false, 
                'Erro', 
                truncateCode(code), 
                timeString,
                errorMessage
            );
        })
        .finally(() => {
            showLoading(false);
            console.log('=== FIM DA VALIDAÇÃO ===\n');
        });
    }
    
    // Função auxiliar para atualizar a interface
    function updateLocalUI(code, data, now, timeString) {
        try {
            // Atualiza a tabela de passes
            if (elements.passesTableBody) {
                const rows = elements.passesTableBody.querySelectorAll('tr');
                const apiCode = (data.codigo || '').toString().replace(/-/g, '').toLowerCase();
                const inputCode = String(code).replace(/-/g, '').toLowerCase();
                
                rows.forEach(tr => {
                    const codeEl = tr.querySelector('.code-cell .code-value');
                    const lastValCell = tr.querySelector('td:nth-child(3)');
                    
                    if (codeEl && lastValCell) {
                        const rowCode = (codeEl.textContent || '').trim();
                        const rowCodeNorm = rowCode.replace(/-/g, '').toLowerCase();
                        
                        if (rowCodeNorm === apiCode || rowCodeNorm === inputCode) {
                            lastValCell.innerHTML = `
                                ${now.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' })}
                                ${timeString}
                                <span class="status-badge success">Válido</span>
                            `;
                        }
                    }
                });
            }
    
            // Atualiza o histórico de validações
            if (elements.validationsList) {
                const item = document.createElement('div');
                item.className = 'validation-item';
                const displayName = (data.usuario && (data.usuario.nome || data.usuario.email)) || 'Usuário';
                
                item.innerHTML = `
                    <div class="validation-icon">
                        <i class="icon-check"></i>
                    </div>
                    <div class="validation-details">
                        <h4>${displayName}</h4>
                        <div class="validation-meta">
                            <span class="validation-time">
                                <i class="icon-clock"></i>
                                ${now.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' })} ${timeString}
                            </span>
                            <span class="validation-status status-success">Válido</span>
                        </div>
                    </div>
                `;
    
                // Remove mensagem de estado vazio se existir
                const emptyState = elements.validationsList.querySelector('.empty-state');
                if (emptyState) {
                    emptyState.remove();
                }
    
                // Adiciona a nova validação no início da lista
                elements.validationsList.prepend(item);
    
                // Atualiza o contador
                if (elements.recentValidationsCount) {
                    const current = parseInt(elements.recentValidationsCount.textContent || '0', 10) || 0;
                    elements.recentValidationsCount.textContent = current + 1;
                }
            }
        } catch (e) {
            console.error('Erro ao atualizar a interface:', e);
        }
    }
    
    // Função auxiliar para obter o token CSRF
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

    // Mostra o resultado da validação em um modal
    function showValidationResult(success, user, code, time, errorMessage = '') {
        if (!elements.modal) return;
        
        // Atualiza o conteúdo do modal com base no resultado
        if (success) {
            elements.modalTitle.textContent = 'Validação Realizada';
            elements.validationResult.className = 'validation-result success';
            elements.validationResult.innerHTML = `
                <div class="result-icon">
                    <i class="material-icons">check_circle</i>
                </div>
                <div class="result-details">
                    <h4>Passe Válido</h4>
                    <p>O passe foi validado com sucesso.</p>
                </div>
            `;
        } else {
            elements.modalTitle.textContent = 'Falha na Validação';
            elements.validationResult.className = 'validation-result error';
            elements.validationResult.innerHTML = `
                <div class="result-icon">
                    <i class="material-icons">error</i>
                </div>
                <div class="result-details">
                    <h4>Passe Inválido</h4>
                    <p>${errorMessage || 'Não foi possível validar o passe.'}</p>
                </div>
            `;
        }
        
        // Preenche as informações
        elements.modalUser.textContent = user;
        elements.modalCode.textContent = code;
        elements.modalDateTime.textContent = time;
        
        // Mostra o modal
        elements.modal.classList.add('show');
        document.body.style.overflow = 'hidden';
    }

    // Fecha o modal
    function closeModal() {
        if (!elements.modal) return;
        
        elements.modal.classList.remove('show');
        document.body.style.overflow = '';
        
        // Pequeno atraso para permitir a animação
        setTimeout(() => {
            elements.modal.style.display = 'none';
        }, 300);
    }

    // Mostra/oculta o indicador de carregamento
    function showLoading(show) {
        const loadingElement = document.createElement('div');
        loadingElement.className = 'loading-overlay';
        loadingElement.innerHTML = `
            <div class="loading-spinner"></div>
            <p>Processando...</p>
        `;
        
        if (show) {
            document.body.appendChild(loadingElement);
        } else {
            const existingLoader = document.querySelector('.loading-overlay');
            if (existingLoader) {
                existingLoader.remove();
            }
        }
    }

    // Funções auxiliares
    function truncateCode(code, maxLength = 20) {
        if (!code) return '';
        if (code.length <= maxLength) return code;
        return `${code.substring(0, maxLength / 2)}...${code.substring(code.length - (maxLength / 2) + 3)}`;
    }

    // Inicialização única
    console.log('Inicializando app (chamada única dentro do DOMContentLoaded)');
    init();
    initClipboard();
    updateDateTime();
    setInterval(updateDateTime, 60000);
});