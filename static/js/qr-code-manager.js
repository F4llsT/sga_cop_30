// qr-code-manager.js - Gerenciador do QR Code (Otimizado)

// Constantes
const QR_UPDATE_INTERVAL = 30000; // 30 segundos
const DEBOUNCE_TIME = 1000; // 1 segundo

// Variáveis globais
let qrCodeScanned = false;
let qrCodeValidationTimer = null;
let isPageVisible = true;
let isGeneratingQR = false;
let qrGenerationQueue = [];
let lastQRUpdate = 0;
let qrImage = null;
let toggleButton = null;
let container = null;

// Inicialização quando o DOM estiver pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initQrCodeManager);
} else {
    initQrCodeManager();
}

function initQrCodeManager() {
    // Obtém os elementos do DOM
    toggleButton = document.getElementById('toggleQrCode');
    container = document.getElementById('qrCodeContainer');
    qrImage = document.getElementById('qrCodeImage');
    const qrCodeUrl = "/passefacil/gerar-qr-code/";
    
    console.log('QR Code Manager inicializado (Otimizado)');
    
    // Inicializa os listeners
    initEventListeners(qrCodeUrl);
    
    // Configura os eventos da imagem do QR Code
    setupQrImageEvents();
    
    // Carrega o QR Code inicial com um pequeno atraso
    if (container) {
        // Garante que o contêiner está oculto inicialmente
        container.style.display = 'none';
    }
}

// Função para inicializar os event listeners
function initEventListeners(qrCodeUrl) {
    // Configura o evento de clique no botão
    if (toggleButton) {
        let lastClickTime = 0;
        
        toggleButton.addEventListener('click', function() {
            const now = Date.now();
            
            // Debounce para evitar múltiplos cliques rápidos
            if (now - lastClickTime < DEBOUNCE_TIME) {
                console.debug('Clique muito rápido, ignorando...');
                return;
            }
            
            lastClickTime = now;
            
            // Se já está gerando, adiciona à fila
            if (isGeneratingQR) {
                console.debug('Adicionando à fila de geração...');
                qrGenerationQueue.push(() => loadQRCode(qrCodeUrl, true));
                return;
            }
            
            // Reseta o estado de validação
            qrCodeScanned = false;
            
            // Mostra o contêiner do QR Code se estiver oculto
            if (container) {
                container.style.display = 'block';
                // Força o navegador a renderizar a mudança
                void container.offsetHeight;
            }
            
            // Atualiza o QR Code
            console.debug('Atualizando QR Code...');
            loadQRCode(qrCodeUrl, true);
        });
    }
    
    // Verifica a visibilidade da página
    document.addEventListener('visibilitychange', handleVisibilityChange);
}

// Função para processar a fila de geração de QR Code
function processQRCodeQueue() {
    if (qrGenerationQueue.length > 0 && !isGeneratingQR) {
        const nextAction = qrGenerationQueue.shift();
        if (typeof nextAction === 'function') {
            nextAction();
        }
    }
}

// Função para carregar o QR Code
function loadQRCode(qrCodeUrl, force = false) {
    const now = Date.now();
    
    // Se já está gerando, adiciona à fila se não for forçado
    if (isGeneratingQR && !force) {
        console.debug('Geração de QR Code já em andamento. Adicionando à fila...');
        qrGenerationQueue.push(() => loadQRCode(qrCodeUrl, true));
        return;
    }
    
    // Se não for forçado e o último update foi recente, não faz nada
    if (!force && (now - lastQRUpdate < QR_UPDATE_INTERVAL)) {
        console.debug('Atualização de QR Code muito recente. Ignorando...');
        return;
    }
    
    console.log('Carregando QR Code...');
    showLoading();
    isGeneratingQR = true;
    
    // Garante que o contêiner do QR Code está visível
    if (!container) {
        container = document.getElementById('qrCodeContainer');
        if (!container) {
            console.error('Contêiner do QR Code não encontrado');
            hideLoading();
            isGeneratingQR = false;
            return;
        }
    }
    
    // Garante que o contêiner está visível
    container.style.display = 'block';
    
    // Obtém ou cria a imagem do QR Code
    if (!qrImage) {
        qrImage = document.getElementById('qrCodeImage');
        if (!qrImage) {
            console.error('Elemento de imagem do QR Code não encontrado');
            hideLoading();
            isGeneratingQR = false;
            return;
        }
    }
    
    // Configura os eventos da imagem se ainda não estiverem configurados
    if (!qrImage.onload) {
        qrImage.onload = function() {
            console.debug('QR Code carregado com sucesso!');
            hideLoading();
            isGeneratingQR = false;
            
            // Anima a transição
            requestAnimationFrame(() => {
                qrImage.style.opacity = '0';
                qrImage.style.transition = 'opacity 0.3s ease-in-out';
                
                requestAnimationFrame(() => {
                    qrImage.style.opacity = '1';
                });
            });
            
            // Dispara evento de QR Code gerado
            setTimeout(() => {
                try {
                    const event = new CustomEvent('qrCodeGenerated', { 
                        detail: { 
                            success: true,
                            timestamp: new Date().toISOString()
                        } 
                    });
                    document.dispatchEvent(event);
                    
                    // Inicia a verificação periódica
                    startQRCodeValidationCheck();
                } catch (e) {
                    console.error('Erro ao processar QR Code:', e);
                }
                
                // Processa a próxima requisição na fila
                processQRCodeQueue();
            }, 0);
        };
        
        // Tratamento de erro
        qrImage.onerror = function(error) {
            console.error('Erro ao carregar o QR Code:', error);
            hideLoading();
            isGeneratingQR = false;
            
            const qrStatus = document.getElementById('qrStatus');
            if (qrStatus) {
                qrStatus.textContent = 'Erro ao gerar o código';
                qrStatus.style.color = '#e74c3c';
            }
            
            showToast('Erro ao carregar o QR Code. Tente novamente.', 'error');
            processQRCodeQueue();
        };
    }
    
    // Adiciona um timestamp para evitar cache e carrega a imagem
    const timestamp = Date.now();
    qrImage.src = `${qrCodeUrl}?t=${timestamp}`;
}

// Função para mostrar o loading
function showLoading() {
    const loadingOverlay = document.getElementById('loadingOverlay');
    const qrStatus = document.getElementById('qrStatus');
    
    if (loadingOverlay) {
        loadingOverlay.style.display = 'flex';
        if (qrStatus) {
            qrStatus.textContent = 'Gerando código...';
            qrStatus.style.color = '';
        }
    }
}

// Função para esconder o loading
function hideLoading() {
    const loadingOverlay = document.getElementById('loadingOverlay');
    const qrStatus = document.getElementById('qrStatus');
    
    if (loadingOverlay) {
        loadingOverlay.style.display = 'none';
        if (qrStatus && !qrCodeScanned) {
            qrStatus.textContent = 'Pronto para uso';
            qrStatus.style.color = '';
        }
    }
}

// Função para lidar com mudanças na visibilidade da página
function handleVisibilityChange() {
    isPageVisible = document.visibilityState === 'visible';
    
    if (isPageVisible) {
        // Se a página ficou visível, retoma a verificação
        startQRCodeValidationCheck();
    } else if (qrCodeValidationTimer) {
        // Se a página ficou oculta, pausa a verificação
        clearInterval(qrCodeValidationTimer);
        qrCodeValidationTimer = null;
    }
}

// Função para iniciar a verificação de validação do QR Code
function startQRCodeValidationCheck() {
    // Limpa qualquer timer existente
    if (qrCodeValidationTimer) {
        clearInterval(qrCodeValidationTimer);
        qrCodeValidationTimer = null;
    }
    
    // Se o QR já foi escaneado ou a página não está visível, não inicia o timer
    if (qrCodeScanned || !isPageVisible) return;
    
    // Verificação menos frequente - a cada 30 segundos
    qrCodeValidationTimer = setInterval(() => {
        // Só executa se a página estiver visível
        if (document.visibilityState === 'visible') {
            console.debug('Verificando status do QR Code...');
            // Código de verificação real viria aqui
        }
    }, QR_UPDATE_INTERVAL);
}

// Função para mostrar notificações toast
function showToast(message, type = 'info') {
    // Verifica se já existe um container de notificações
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.style.position = 'fixed';
        container.style.top = '20px';
        container.style.right = '20px';
        container.style.zIndex = '1000';
        document.body.appendChild(container);
    }
    
    // Cria o elemento da notificação
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.style.padding = '12px 20px';
    toast.style.marginBottom = '10px';
    toast.style.borderRadius = '4px';
    toast.style.color = 'white';
    toast.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
    toast.style.opacity = '0';
    toast.style.transition = 'opacity 0.3s ease-in-out';
    toast.textContent = message;
    
    // Define a cor de fundo com base no tipo
    const colors = {
        'success': '#27ae60',
        'error': '#e74c3c',
        'info': '#3498db',
        'warning': '#f39c12'
    };
    toast.style.backgroundColor = colors[type] || colors['info'];
    
    // Adiciona a notificação ao container
    container.appendChild(toast);
    
    // Anima a entrada
    setTimeout(() => {
        toast.style.opacity = '1';
    }, 10);
    
    // Remove a notificação após 5 segundos
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, 5000);
}

// Função para configurar os eventos da imagem do QR Code
function setupQrImageEvents() {
    if (!qrImage) {
        qrImage = document.getElementById('qrCodeImage');
    }
    
    if (qrImage && !qrImage.onload) {
        qrImage.onload = function() {
            console.debug('QR Code carregado com sucesso!');
            hideLoading();
            isGeneratingQR = false;
            
            // Anima a transição
            requestAnimationFrame(() => {
                qrImage.style.opacity = '0';
                qrImage.style.transition = 'opacity 0.3s ease-in-out';
                
                requestAnimationFrame(() => {
                    qrImage.style.opacity = '1';
                });
            });
            
            // Dispara evento de QR Code gerado
            setTimeout(() => {
                try {
                    const event = new CustomEvent('qrCodeGenerated', { 
                        detail: { 
                            success: true,
                            timestamp: new Date().toISOString()
                        } 
                    });
                    document.dispatchEvent(event);
                    
                    // Inicia a verificação periódica
                    startQRCodeValidationCheck();
                } catch (e) {
                    console.error('Erro ao processar QR Code:', e);
                }
                
                // Processa a próxima requisição na fila
                processQRCodeQueue();
            }, 0);
        };
        
        // Tratamento de erro
        qrImage.onerror = function(error) {
            console.error('Erro ao carregar o QR Code:', error);
            hideLoading();
            isGeneratingQR = false;
            
            const qrStatus = document.getElementById('qrStatus');
            if (qrStatus) {
                qrStatus.textContent = 'Erro ao gerar o código';
                qrStatus.style.color = '#e74c3c';
            }
            
            showToast('Erro ao carregar o QR Code. Tente novamente.', 'error');
            processQRCodeQueue();
        };
    }
}

// Exporta funções para uso global
window.QRCodeManager = {
    init: initQrCodeManager,
    showToast: showToast,
    // Adiciona uma função para forçar a validação (para testes)
    forceValidation: function(location = 'Ponto de Controle') {
        const event = new CustomEvent('qrCodeValidated', {
            detail: {
                valid: true,
                timestamp: new Date().toISOString(),
                location: location,
                isNew: true
            }
        });
        document.dispatchEvent(event);
    }
};