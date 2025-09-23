// Função para verificar se o usuário tem notificações de validação pendentes
function checkForValidations() {
    // Verifica se o usuário está na página do QR Code
    if (!document.getElementById('qrStatus')) return;
    
    // Faz uma requisição para verificar validações recentes
    // Usa credentials: 'same-origin' para incluir os cookies de sessão
    fetch('/api/passefacil/ultimas-validacoes/', {
        method: 'GET',
        credentials: 'same-origin' // Importante: inclui os cookies de autenticação
    })
    .then(response => {
        if (!response.ok) {
            if (response.status === 401) {
                console.log('Usuário não autenticado. Redirecionando para login...');
                // Redireciona para a página de login, mantendo a URL atual para redirecionamento posterior
                window.location.href = '/login/?next=' + encodeURIComponent(window.location.pathname);
                return null;
            }
            throw new Error('Erro na requisição: ' + response.status);
        }
        return response.json();
    })
    .then(data => {
        if (!data) return; // Se data for null (usuário não autenticado), sai da função
            if (data.validacoes && data.validacoes.length > 0) {
                // Dispara eventos para cada validação recente
                data.validacoes.forEach(validacao => {
                    const event = new CustomEvent('qrCodeValidated', {
                        detail: {
                            valid: validacao.valido,
                            timestamp: validacao.data_validacao,
                            location: validacao.ip_address || 'Local desconhecido'
                        }
                    });
                    document.dispatchEvent(event);
                });
            }
        })
        .catch(error => console.error('Erro ao verificar validações:', error));
}

// Verifica por validações a cada 30 segundos
setInterval(checkForValidations, 30000);

// Verifica por validações quando a página é carregada
document.addEventListener('DOMContentLoaded', function() {
    // Verifica após um pequeno atraso para garantir que o DOM esteja totalmente carregado
    setTimeout(checkForValidations, 2000);
    
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
