// Função para obter o token JWT do armazenamento local ou cookie
function getAuthToken() {
    // Tenta obter do armazenamento local
    const token = localStorage.getItem('access_token') || getCookie('access_token');
    return token ? `Bearer ${token}` : null;
}

// Função para verificar se o usuário tem notificações de validação pendentes
function checkForValidations() {
    // Verifica se o usuário está na página do QR Code
    if (!document.getElementById('qrStatus')) return;
    
    const token = getAuthToken();
    if (!token) {
        console.log('Usuário não autenticado. Ignorando verificação de validações.');
        return;
    }
    
    // Configuração do cabeçalho com o token JWT
    const headers = new Headers({
        'Content-Type': 'application/json',
        'Authorization': token
    });
    
    // Faz uma requisição para verificar validações recentes
    fetch('/api/passefacil/ultimas-validacoes/', {
        method: 'GET',
        headers: headers,
        credentials: 'same-origin' // Inclui cookies na requisição
    })
    .then(response => {
        if (!response.ok) {
            if (response.status === 401) {
                console.error('Erro de autenticação: Token inválido ou expirado');
                // Opcional: redirecionar para a página de login
                // window.location.href = '/login/?next=' + encodeURIComponent(window.location.pathname);
            }
            throw new Error('Erro na requisição: ' + response.status);
        }
        return response.json();
    })
    .then(data => {
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
