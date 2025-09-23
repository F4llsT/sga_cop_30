// qr-code-manager.js - Gerenciador do QR Code

document.addEventListener('DOMContentLoaded', function() {
    const toggleButton = document.getElementById('toggleQrCode');
    const container = document.getElementById('qrCodeContainer');
    const qrImage = document.getElementById('qrCodeImage');
    const qrCodeUrl = "/passefacil/gerar-qr-code/"; // URL direta para evitar problemas com a tag de template
    
    console.log('QR Code Manager carregado');
    
    // Adiciona um timestamp para evitar cache
    function getQrCodeUrl() {
        return `${qrCodeUrl}?t=${new Date().getTime()}`;
    }
    
    // Inicialmente esconde o container do QR Code
    if (container) container.style.display = 'none';
    
    // Função para mostrar o loading
    function showLoading() {
        const loadingOverlay = document.getElementById('loadingOverlay');
        const qrStatus = document.getElementById('qrStatus');
        if (loadingOverlay) {
            loadingOverlay.style.display = 'flex';
            if (qrStatus) {
                qrStatus.textContent = 'Gerando novo código...';
                qrStatus.style.color = '#e67e22';
            }
        }
    }
    
    // Função para esconder o loading
    function hideLoading() {
        const loadingOverlay = document.getElementById('loadingOverlay');
        const qrStatus = document.getElementById('qrStatus');
        if (loadingOverlay) {
            loadingOverlay.style.display = 'none';
            if (qrStatus) {
                qrStatus.textContent = 'Pronto para uso';
                qrStatus.style.color = '#27ae60';
            }
        }
    }
    
    // Função para carregar o QR Code
    function loadQRCode() {
        console.log('Carregando QR Code...');
        showLoading();
        
        // Atualiza a URL com um timestamp para evitar cache
        const timestamp = new Date().getTime();
        qrImage.src = getQrCodeUrl() + '&t=' + timestamp;
        
        // Mostra o container
        container.style.display = 'block';
        
        // Atualiza o texto do botão
        if (toggleButton) {
            toggleButton.innerHTML = '<i class="fas fa-sync-alt me-2"></i> Atualizar QR Code';
        }
        
        // Atualiza a data/hora da última atualização
        const now = new Date();
        const lastUpdated = document.getElementById('lastUpdated');
        if (lastUpdated) {
            lastUpdated.textContent = `Hoje às ${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}`;
        }
    }
    
    // Configura o evento de clique no botão
    if (toggleButton) {
        toggleButton.addEventListener('click', function() {
            console.log('Botão clicado');
            
            if (container.style.display === 'none' || !container.style.display) {
                loadQRCode();
            } else {
                console.log('Atualizando QR Code...');
                loadQRCode();
            }
        });
    }
    
    // Configura os eventos da imagem do QR Code
    if (qrImage) {
        // Quando a imagem carregar
        qrImage.onload = function() {
            console.log('QR Code carregado com sucesso!');
            hideLoading();
            
            // Adiciona uma classe de animação suave
            qrImage.style.opacity = '0';
            setTimeout(() => {
                qrImage.style.transition = 'opacity 0.3s ease-in-out';
                qrImage.style.opacity = '1';
            }, 100);
            
            // Dispara evento personalizado
            const event = new CustomEvent('qrCodeGenerated', { detail: { success: true } });
            document.dispatchEvent(event);
        };
        
        // Tratamento de erro
        qrImage.onerror = function(error) {
            console.error('Erro ao carregar o QR Code:', error);
            hideLoading();
            
            const qrStatus = document.getElementById('qrStatus');
            if (qrStatus) {
                qrStatus.textContent = 'Erro ao gerar o código';
                qrStatus.style.color = '#e74c3c';
            }
            
            if (qrImage) {
                qrImage.alt = 'Erro ao carregar o QR Code';
            }
            
            // Mostra notificação de erro
            const event = new CustomEvent('qrCodeGenerated', { detail: { success: false, error: error } });
            document.dispatchEvent(event);
            
            // Tenta recarregar após 2 segundos
            setTimeout(() => {
                showLoading();
                if (qrImage) {
                    qrImage.src = getQrCodeUrl() + '&t=' + new Date().getTime();
                }
            }, 2000);
        };
    }
    
    // Função para atualizar a lista de validações recentes
    window.updateRecentValidations = function() {
        console.log('Atualizando histórico de validações...');
        // Implemente a lógica para buscar validações recentes aqui
    };
    
    // Configura o evento de validação do QR Code
    document.addEventListener('qrCodeValidated', function(event) {
        const { valid, timestamp, location } = event.detail;
        const statusElement = document.getElementById('qrStatus');
        
        if (statusElement) {
            if (valid) {
                statusElement.textContent = `Validado em ${new Date(timestamp).toLocaleString()}`;
                statusElement.style.color = '#27ae60';
                
                // Mostra a animação de sucesso
                if (typeof onQRCodeValidated === 'function') {
                    onQRCodeValidated({
                        location: location || 'Ponto de Controle',
                        timestamp: timestamp || new Date().toISOString()
                    });
                }
                
                // Mostra notificação de sucesso
                showToast('Seu código foi validado com sucesso!', 'success');
            } else {
                statusElement.textContent = 'Tentativa de validação inválida';
                statusElement.style.color = '#e74c3c';
                
                // Mostra notificação de erro
                showToast('Tentativa de validação inválida detectada', 'error');
            }
        }
        
        // Atualiza a lista de validações recentes
        updateRecentValidations();
    });
    
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
            container.style.zIndex = '9999';
            document.body.appendChild(container);
        }
        
        // Cria o elemento da notificação
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.style.padding = '12px 20px';
        toast.style.marginBottom = '10px';
        toast.style.borderRadius = '4px';
        toast.style.color = 'white';
        toast.style.backgroundColor = type === 'success' ? '#27ae60' : type === 'error' ? '#e74c3c' : '#3498db';
        toast.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.3s ease-in-out';
        toast.textContent = message;
        
        // Adiciona a notificação ao container
        container.appendChild(toast);
        
        // Mostra a notificação com animação
        setTimeout(() => {
            toast.style.opacity = '1';
        }, 100);
        
        // Remove a notificação após 5 segundos
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => {
                toast.remove();
            }, 300);
        }, 5000);
    }
});
