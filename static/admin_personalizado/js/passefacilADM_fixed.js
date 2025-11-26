/**
 * Passe Fácil - Painel de Administração
 * Script principal para funcionalidades do painel
 * Versão: 3.1 - Corrigido problema do Chart.js
 */

class PasseFacilAdmin {
    constructor() {
        this.elements = this.initializeElements();
        this.state = this.initializeState();
        this.initialize();
    }

    /**
     * Inicializa os elementos da interface
     */
    initializeElements() {
        return {
            // Navegação
            listView: document.getElementById('listView'),
            listViewBtn: document.getElementById('listViewBtn'),
            validateViewBtn: document.getElementById('validateViewBtn'),
            
            // Lista de passes
            passesTableBody: document.getElementById('passesTableBody'),
            searchInput: document.getElementById('searchInput'),
            totalResults: document.getElementById('totalResults'),
            
            // Validação
            validateView: document.getElementById('validateView'),
            manualCodeInput: document.getElementById('manualCodeInput'),
            validateManualBtn: document.getElementById('validateManualBtn'),
            toggleCameraBtn: document.getElementById('toggleCameraBtn'),
            cameraFeed: document.getElementById('cameraFeed'),
            
            // Abas
            tabButtons: document.querySelectorAll('.tab-btn'),
            tabPanes: document.querySelectorAll('.tab-pane'),
            qrTab: document.getElementById('qrTab'),
            manualTab: document.getElementById('manualTab'),
            
            // Modal
            modal: document.getElementById('validationModal'),
            closeModal: document.querySelector('.close-modal'),
            closeModalBtn: document.getElementById('closeModalBtn'),
            newValidationBtn: document.getElementById('newValidationBtn'),
            modalTitle: document.getElementById('modalTitle'),
            validationResult: document.getElementById('validationResult'),
            modalUser: document.getElementById('modalUser'),
            modalCode: document.getElementById('modalCode'),
            modalDateTime: document.getElementById('modalDateTime'),
            
            // Gráfico
            miniChart: document.getElementById('miniChart'),
            
            // Histórico
            validationsList: document.getElementById('validationsList'),
            recentValidationsCount: document.getElementById('recentValidationsCount')
        };
    }

    /**
     * Inicializa o estado da aplicação
     */
    initializeState() {
        return {
            currentView: 'list',
            currentTab: 'qrTab',
            isCameraActive: false,
            mediaStream: null,
            chart: null,
            searchTimeout: null,
            chartInitialized: false
        };
    }

    /**
     * Inicialização principal da aplicação
     */
    initialize() {
        console.log('=== INICIALIZAÇÃO DO SISTEMA ===');
        this.setupEventListeners();
        
        // Inicializa o gráfico após um pequeno delay para garantir que o DOM está pronto
        setTimeout(() => {
            this.initChart();
        }, 100);
        
        this.updateDateTime();
        this.showView('list');
        
        // Atualiza a data/hora a cada minuto
        setInterval(() => this.updateDateTime(), 60000);
    }

    /**
     * Configura os event listeners
     */
    setupEventListeners() {
        const { elements } = this;
        
        // Navegação
        if (elements.listViewBtn) {
            elements.listViewBtn.addEventListener('click', () => this.showView('list'));
        }
        
        if (elements.validateViewBtn) {
            elements.validateViewBtn.addEventListener('click', () => this.showView('validate'));
        }
        
        // Busca
        if (elements.searchInput) {
            elements.searchInput.addEventListener('input', (e) => this.handleSearch(e));
        }
        
        // Validação manual
        if (elements.manualCodeInput) {
            elements.manualCodeInput.addEventListener('input', () => this.toggleValidateButton());
            elements.manualCodeInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && elements.validateManualBtn && !elements.validateManualBtn.disabled) {
                    this.validateManualCode();
                }
            });
        }
        
        if (elements.validateManualBtn) {
            elements.validateManualBtn.addEventListener('click', () => this.validateManualCode());
        }
        
        // Câmera
        if (elements.toggleCameraBtn) {
            elements.toggleCameraBtn.addEventListener('click', () => this.toggleCamera());
        }
        
        // Abas
        elements.tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const tabId = button.getAttribute('data-tab');
                this.showTab(tabId);
            });
        });
        
        // Modal
        if (elements.closeModal) {
            elements.closeModal.addEventListener('click', () => this.closeModal());
        }
        
        if (elements.closeModalBtn) {
            elements.closeModalBtn.addEventListener('click', () => this.closeModal());
        }
        
        if (elements.newValidationBtn) {
            elements.newValidationBtn.addEventListener('click', () => {
                this.closeModal();
                this.showView('validate');
            });
        }
        
        // Fecha o modal ao clicar fora
        window.addEventListener('click', (e) => {
            if (e.target === elements.modal) {
                this.closeModal();
            }
        });
        
        // Limpa recursos ao fechar a página
        window.addEventListener('beforeunload', () => this.cleanup());
    }

    /**
     * Limpa recursos da aplicação
     */
    cleanup() {
        if (this.state.mediaStream) {
            this.state.mediaStream.getTracks().forEach(track => track.stop());
            this.state.mediaStream = null;
        }
        
        if (this.state.chart) {
            this.state.chart.destroy();
            this.state.chart = null;
        }
    }

    /**
     * Alterna entre as views (lista/validação)
     */
    showView(viewName) {
        console.log('Mostrando view:', viewName);
        const { elements, state } = this;
        state.currentView = viewName;
        
        // Atualiza a UI
        if (elements.listView) elements.listView.classList.toggle('active', viewName === 'list');
        if (elements.validateView) elements.validateView.classList.toggle('active', viewName === 'validate');
        
        // Atualiza os botões de navegação
        if (elements.listViewBtn) elements.listViewBtn.classList.toggle('active', viewName === 'list');
        if (elements.validateViewBtn) elements.validateViewBtn.classList.toggle('active', viewName === 'validate');
        
        // Gerencia o estado da câmera
        if (viewName !== 'validate' && state.isCameraActive) {
            this.toggleCamera();
        }
        
        if (viewName === 'validate' && elements.validateView) {
            this.showTab(state.currentTab);
        }
    }

    /**
     * Alterna entre as abas (QR Code / Código Manual)
     */
    showTab(tabId) {
        console.log('Mostrando aba:', tabId);
        const { elements, state } = this;
        state.currentTab = tabId;
        
        // Atualiza os botões das abas
        elements.tabButtons.forEach(btn => {
            const isActive = btn.getAttribute('data-tab') === tabId;
            btn.classList.toggle('active', isActive);
        });
        
        // Mostra o conteúdo da aba ativa
        elements.tabPanes.forEach(pane => {
            pane.classList.toggle('active', pane.id === tabId);
        });
        
        // Gerencia o estado da câmera
        if (tabId === 'qrTab' && state.isCameraActive) {
            this.initCamera();
        } else if (tabId !== 'qrTab' && state.isCameraActive) {
            this.toggleCamera();
        }
    }

    /**
     * Habilita/desabilita o botão de validar com base no input
     */
    toggleValidateButton() {
        const { elements } = this;
        if (elements.validateManualBtn) {
            elements.validateManualBtn.disabled = !elements.manualCodeInput?.value.trim();
        }
    }

    /**
     * Valida um código manualmente
     */
    validateManualCode() {
        const { elements } = this;
        const code = elements.manualCodeInput?.value.trim();
        if (code) {
            this.validateCode(code);
            elements.manualCodeInput.value = '';
            elements.validateManualBtn.disabled = true;
        }
    }

    /**
     * Alterna o estado da câmera (ligar/desligar)
     */
    async toggleCamera() {
        const { state, elements } = this;
        
        if (state.isCameraActive) {
            // Desativa a câmera
            if (state.mediaStream) {
                state.mediaStream.getTracks().forEach(track => track.stop());
                state.mediaStream = null;
            }
            
            if (elements.cameraFeed) {
                elements.cameraFeed.innerHTML = `
                    <div class="scanner-frame">
                        <div class="scanner-corner top-left"></div>
                        <div class="scanner-corner top-right"></div>
                        <div class="scanner-corner bottom-left"></div>
                        <div class="scanner-corner bottom-right"></div>
                    </div>
                    <p class="camera-hint">Posicione o QR Code dentro da área destacada</p>
                `;
            }
            
            if (elements.toggleCameraBtn) {
                elements.toggleCameraBtn.innerHTML = '<i class="icon-camera"></i><span>Iniciar Câmera</span>';
            }
            
            state.isCameraActive = false;
        } else {
            // Ativa a câmera
            await this.initCamera();
        }
    }

    /**
     * Inicializa a câmera para leitura de QR Code
     */
    async initCamera() {
        const { elements, state } = this;
        
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ 
                video: { 
                    facingMode: 'environment',
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                } 
            });
            
            state.mediaStream = stream;
            state.isCameraActive = true;
            
            if (elements.cameraFeed) {
                elements.cameraFeed.innerHTML = `
                    <video id="qr-video" autoplay playsinline></video>
                    <canvas id="qr-canvas" style="display: none;"></canvas>
                `;
                const video = elements.cameraFeed.querySelector('#qr-video');
                const canvas = elements.cameraFeed.querySelector('#qr-canvas');
                const canvasContext = canvas.getContext('2d');
                
                video.srcObject = stream;
                
                // Set canvas dimensions to match video
                video.onloadedmetadata = () => {
                    canvas.width = video.videoWidth;
                    canvas.height = video.videoHeight;
                };
                
                // QR Code scanning function
                const scanQRCode = () => {
                    if (!state.isCameraActive) return;
                    
                    if (video.readyState === video.HAVE_ENOUGH_DATA) {
                        // Draw video frame to canvas
                        canvasContext.drawImage(video, 0, 0, canvas.width, canvas.height);
                        
                        // Get image data from canvas
                        const imageData = canvasContext.getImageData(0, 0, canvas.width, canvas.height);
                        
                        // Try to decode QR code
                        try {
                            const code = jsQR(imageData.data, imageData.width, imageData.height, {
                                inversionAttempts: 'dontInvert',
                            });
                            
                            // If QR code is found
                            if (code) {
                                console.log('QR Code detected:', code.data);
                                this.validateCode(code.data);
                                // Pause scanning after successful detection
                                this.toggleCamera();
                            }
                        } catch (e) {
                            console.error('Error scanning QR code:', e);
                        }
                    }
                    
                    // Continue scanning
                    if (state.isCameraActive) {
                        requestAnimationFrame(scanQRCode);
                    }
                };
                
                // Start scanning
                video.play().then(() => {
                    scanQRCode();
                }).catch(err => {
                    console.error('Error starting video:', err);
                    this.showNotification('error', 'Erro ao iniciar a câmera');
                });
            }
            
            if (elements.toggleCameraBtn) {
                elements.toggleCameraBtn.innerHTML = '<i class="icon-camera-off"></i><span>Desligar Câmera</span>';
                elements.toggleCameraBtn.disabled = false;
            }
            
        } catch (err) {
            console.error('Erro ao acessar a câmera:', err);
            this.showNotification('error', 'Não foi possível acessar a câmera. Verifique as permissões do navegador.');
            if (elements.toggleCameraBtn) {
                elements.toggleCameraBtn.innerHTML = '<i class="icon-camera"></i><span>Tentar Novamente</span>';
                elements.toggleCameraBtn.disabled = false;
            }
        }
    }

    /**
     * Valida um código (QR Code ou manual)
     */
    async validateCode(code) {
        if (!code) {
            console.error('Nenhum código fornecido para validação');
            return;
        }
        
        const { elements } = this;
        this.showLoading(true);
        
        try {
            const response = await fetch(`/passefacil/api/validar-qr-code/?codigo=${encodeURIComponent(code)}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin'
            });
            
            const data = await response.json();
            this.showLoading(false);
            
            if (data.valido) {
                this.showValidationResult(true, data.usuario || 'Usuário', code, new Date().toLocaleTimeString(), data.mensagem || 'Código válido');
                // Atualiza a interface com o novo código validado
                this.updateLocalUI(code, data, new Date(), new Date().toLocaleTimeString());
            } else {
                this.showValidationResult(false, 'Código inválido', code, new Date().toLocaleTimeString(), data.mensagem || 'Código inválido ou expirado');
            }
            
        } catch (error) {
            console.error('Erro na validação:', error);
            this.showLoading(false);
            this.showValidationResult(false, 'Erro', code, new Date().toLocaleTimeString(), 'Erro ao validar o código. Tente novamente.');
        }
    }

    /**
     * Fecha o modal de validação
     */
    closeModal() {
        const { elements } = this;
        if (!elements.modal) return;
        
        elements.modal.classList.remove('show');
        
        // Limpa o resultado da validação
        if (elements.validationResult) {
            elements.validationResult.className = 'validation-result';
        }
        
        // Limpa os campos do modal
        if (elements.modalUser) elements.modalUser.textContent = '--';
        if (elements.modalCode) elements.modalCode.textContent = '--';
        if (elements.modalDateTime) elements.modalDateTime.textContent = '--';
        
        // Reativa a câmera se estiver na aba de QR Code
        if (this.state.currentTab === 'qrTab' && this.state.isCameraActive) {
            this.initCamera();
        }
    }

    /**
     * Mostra o resultado da validação em um modal
     */
    showValidationResult(success, user, code, time, message = '') {
        const { elements } = this;
        if (!elements.modal) return;
        
        // Extrai o nome do usuário (pode ser um objeto ou string)
        const userName = (user && typeof user === 'object' && user.nome) ? 
                        user.nome : 
                        (user || '-');
        
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
                    <p>${message || 'O passe foi validado com sucesso.'}</p>
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
                    <p>${message || 'Não foi possível validar o passe.'}</p>
                </div>
            `;
        }
        
        // Preenche as informações
        elements.modalUser.textContent = userName;
        elements.modalCode.textContent = code || '-';
        elements.modalDateTime.textContent = time || new Date().toLocaleString();
        
        // Mostra o modal
        elements.modal.classList.add('show');
        document.body.style.overflow = 'hidden';
    }

    /**
     * Mostra/oculta o indicador de carregamento
     */
    showLoading(show) {
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

    /**
     * Atualiza a interface do usuário após uma validação bem-sucedida
     */
    updateLocalUI(code, data, now, timeString) {
        const { elements } = this;
        
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

    /**
     * Trunca códigos longos para exibição
     */
    truncateCode(code, maxLength = 20) {
        if (!code) return '';
        if (code.length <= maxLength) return code;
        return `${code.substring(0, maxLength / 2)}...${code.substring(code.length - (maxLength / 2) + 3)}`;
    }

    /**
     * Inicializa o gráfico - VERSÃO CORRIGIDA
     */
    initChart() {
        const { elements, state } = this;
        
        // Evita inicialização duplicada
        if (state.chartInitialized) {
            console.log('Gráfico já foi inicializado');
            return;
        }
        
        if (!elements.miniChart) {
            console.error('Elemento do gráfico não encontrado');
            return;
        }
        
        // Procura pelo canvas dentro do container
        let canvas = elements.miniChart.querySelector('canvas');
        
        if (!canvas) {
            console.log('Canvas não encontrado, o gráfico pode não ter sido criado pelo template ainda');
            // Tenta novamente após um pequeno delay
            setTimeout(() => this.initChart(), 200);
            return;
        }
        
        // Destrói o gráfico existente, se houver
        if (state.chart) {
            state.chart.destroy();
            state.chart = null;
        }
        
        const ctx = canvas.getContext('2d');
        if (!ctx) {
            console.error('Não foi possível obter o contexto 2D do canvas');
            return;
        }
        
        // Marca como inicializado
        state.chartInitialized = true;
        
        // Dados mockados para teste (substituir com dados reais do template)
        state.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'],
                datasets: [{
                    label: 'Validações',
                    data: [12, 19, 3, 5, 2, 3, 10],
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1,
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        enabled: true,
                        mode: 'index',
                        intersect: false
                    }
                },
                scales: {
                    y: { display: false },
                    x: { display: false }
                },
                elements: {
                    point: { radius: 0 }
                }
            }
        });
        
        console.log('Gráfico inicializado com sucesso');
    }

    /**
     * Atualiza a data e hora no cabeçalho
     */
    updateDateTime() {
        const now = new Date();
        const dateTimeElement = document.getElementById('currentDateTime');
        const timeElement = document.getElementById('current-time');
        
        if (dateTimeElement) {
            const options = { 
                weekday: 'long', 
                day: '2-digit', 
                month: 'long', 
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            };
            
            dateTimeElement.textContent = now.toLocaleDateString('pt-BR', options);
        }
        
        // Atualiza o relógio em tempo real
        if (timeElement) {
            timeElement.textContent = now.toLocaleTimeString('pt-BR', {
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            });
        }
    }

    /**
     * Manipula a busca na lista de passes
     */
    handleSearch(e) {
        const { elements } = this;
        const searchTerm = e.target.value.toLowerCase();
        
        if (this.state.searchTimeout) {
            clearTimeout(this.state.searchTimeout);
        }
        
        // Debounce para evitar muitas atualizações durante a digitação
        this.state.searchTimeout = setTimeout(() => {
            if (!elements.passesTableBody) return;
            
            const rows = elements.passesTableBody.querySelectorAll('tr');
            let visibleCount = 0;
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                const isVisible = text.includes(searchTerm);
                row.style.display = isVisible ? '' : 'none';
                if (isVisible) visibleCount++;
            });
            
            if (elements.totalResults) {
                elements.totalResults.textContent = 
                    `${visibleCount} resultado${visibleCount !== 1 ? 's' : ''} encontrado${visibleCount !== 1 ? 's' : ''}`;
            }
        }, 300);
    }

    /**
     * Obtém o valor de um cookie
     */
    getCookie(name) {
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
     * Exibe uma notificação para o usuário
     */
    showNotification(type, message) {
        // Implementação básica - pode ser substituída por uma biblioteca de notificações
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Remove a notificação após 5 segundos
        setTimeout(() => {
            notification.classList.add('fade-out');
            setTimeout(() => notification.remove(), 300);
        }, 5000);
    }
}

// Inicializa a aplicação quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    const app = new PasseFacilAdmin();
    
    // Expõe a instância globalmente se necessário para depuração
    window.passeFacilAdmin = app;
});
