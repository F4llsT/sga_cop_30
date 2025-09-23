// Variável para controlar se já verificamos as validações iniciais
let initialValidationsChecked = false;
let lastValidationId = null;

// Função para verificar se o usuário tem notificações de validação pendentes
let isChecking = false;

async function checkForValidations(isInitialCheck = false) {
    // Verifica se o usuário está na página do QR Code
    if (!document.getElementById('qrStatus') || isChecking) return;
    
    isChecking = true;
    
    // Se for a verificação inicial, apenas marcamos como verificada e não fazemos nada
    if (isInitialCheck) {
        initialValidationsChecked = true;
        return;
    }
    
    // Se for uma verificação subsequente, verificamos apenas validações novas
    fetch('/api/passefacil/ultimas-validacoes/', {
        method: 'GET',
        credentials: 'same-origin'
    })
    .then(response => {
        if (!response.ok) {
            if (response.status === 401) {
                console.log('Usuário não autenticado. Redirecionando para login...');
                window.location.href = '/login/?next=' + encodeURIComponent(window.location.pathname);
                return null;
            }
            throw new Error('Erro na requisição: ' + response.status);
        }
        return response.json();
    })
    .then(data => {
        if (!data || !data.validacoes || data.validacoes.length === 0) return;
        
        // Ordena as validações por data (mais recente primeiro)
        const sortedValidations = [...data.validacoes].sort((a, b) => 
            new Date(b.data_validacao) - new Date(a.data_validacao)
        );
        
        // Pega a validação mais recente
        const latestValidation = sortedValidations[0];
        
        // Se for uma validação nova (diferente da última que vimos)
        if (latestValidation.id !== lastValidationId) {
            lastValidationId = latestValidation.id;
            
            // Só dispara o evento se não for a verificação inicial
            if (initialValidationsChecked) {
                const event = new CustomEvent('qrCodeValidated', {
                    detail: {
                        valid: latestValidation.valido,
                        timestamp: latestValidation.data_validacao,
                        location: latestValidation.ip_address || 'Local desconhecido',
                        isNew: true
                    }
                });
                document.dispatchEvent(event);
            }
        }
    })
    .catch(error => console.error('Erro ao verificar validações:', error))
    .finally(() => {
        isChecking = false;
    });
}

// Variável para controlar o timer de verificação
let validationCheckTimer = null;

// Função para iniciar a verificação periódica
function startValidationChecks() {
    // Limpa qualquer timer existente
    if (validationCheckTimer) {
        clearInterval(validationCheckTimer);
    }
    
    // Verifica a cada 30 segundos (aumentado para reduzir carga)
    validationCheckTimer = setInterval(() => checkForValidations(false), 30000);
}

// Verifica por validações quando a página é carregada
document.addEventListener('DOMContentLoaded', function() {
    // Marca a verificação inicial, mas não dispara notificações
    checkForValidations(true);
    
    // Inicia a verificação periódica após um atraso
    setTimeout(startValidationChecks, 5000);
    
    // Pausa as verificações quando a aba não está visível
    document.addEventListener('visibilitychange', function() {
        if (document.hidden) {
            if (validationCheckTimer) {
                clearInterval(validationCheckTimer);
                validationCheckTimer = null;
            }
        } else {
            // Retoma as verificações quando a aba se torna visível novamente
            if (!validationCheckTimer) {
                startValidationChecks();
                // Força uma verificação imediata ao voltar para a aba
                setTimeout(() => checkForValidations(false), 1000);
            }
        }
    });
    
    // Adiciona um listener para o evento de validação do QR Code
    document.addEventListener('qrCodeValidated', function(event) {
        const { valid, timestamp, location } = event.detail;
        
        if (valid) {
            // Chama a função de animação de sucesso
            if (typeof onQRCodeValidated === 'function') {
                onQRCodeValidated({
                    location: location || 'Ponto de Controle',
                    timestamp: timestamp || new Date().toISOString()
                });
            }
            
            // Atualiza o status do QR Code
            const qrStatus = document.getElementById('qrStatus');
            if (qrStatus) {
                qrStatus.textContent = 'Validado agora há pouco';
                qrStatus.style.color = '#4CAF50';
                qrStatus.style.fontWeight = 'bold';
            }
            
            // Atualiza o horário da última atualização
            const lastUpdated = document.getElementById('lastUpdated');
            if (lastUpdated) {
                const now = new Date(timestamp || new Date());
                const timeString = now.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
                lastUpdated.textContent = `Hoje às ${timeString}`;
            }
        }
    });
    
    // Configura o Service Worker para notificações push
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/service-worker.js')
            .then(registration => {
                console.log('ServiceWorker registration successful');
                return registration.pushManager.getSubscription()
                    .then(subscription => {
                        if (subscription) {
                            return subscription;
                        }
                        // Se não estiver inscrito, tenta se inscrever
                        return registration.pushManager.subscribe({
                            userVisibleOnly: true,
                            applicationServerKey: urlBase64ToUint8Array('{{ VAPID_PUBLIC_KEY }}')
                        });
                    });
            })
            .then(subscription => {
                console.log('Usuário inscrito:', subscription);
                // Aqui você pode enviar a inscrição para o servidor
                return fetch('/api/notificacoes/inscrever/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify(subscription)
                });
            })
            .catch(error => {
                console.error('Erro no ServiceWorker:', error);
            });
    }
});

// Função auxiliar para converter chave VAPID para Uint8Array
function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding).replace(/\-/g, '+').replace(/_/g, '/');
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    
    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}

// Função auxiliar para obter cookies
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
