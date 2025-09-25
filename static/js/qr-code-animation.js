// Função para mostrar a animação de sucesso
function showSuccessAnimation(location = 'Ponto de Controle') {
    const qrCodeImage = document.getElementById('qrCodeImage');
    const successAnimation = document.getElementById('successAnimation');
    const validationTime = document.getElementById('validationTime');
    const validationLocation = document.getElementById('validationLocation');
    
    // Atualiza as informações de tempo e local
    const now = new Date();
    const timeString = now.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
    
    validationTime.textContent = `Hoje às ${timeString}`;
    validationLocation.textContent = `Local: ${location}`;
    
    // Adiciona a classe de validação para o efeito de pulso
    qrCodeImage.classList.add('qr-validated');
    
    // Esconde a imagem do QR Code e mostra a animação
    qrCodeImage.style.display = 'none';
    successAnimation.style.display = 'flex';
    
    // Adiciona confetes
    createConfetti();
    
    // Depois de 5 segundos, volta a mostrar o QR Code
    setTimeout(() => {
        // Remove a classe de validação
        qrCodeImage.classList.remove('qr-validated');
        
        // Esconde a animação e mostra o QR Code novamente
        successAnimation.style.display = 'none';
        qrCodeImage.style.display = 'block';
    }, 5000);
}

// Função para criar efeito de confete
function createConfetti() {
    const colors = ['#4CAF50', '#2196F3', '#FFC107', '#E91E63', '#9C27B0'];
    const container = document.querySelector('.qr-code-wrapper');
    
    // Cria 50 partículas de confete
    for (let i = 0; i < 50; i++) {
        const confetti = document.createElement('div');
        confetti.className = 'confetti';
        
        // Posição aleatória no topo do container
        confetti.style.left = Math.random() * 100 + '%';
        confetti.style.top = '-10px';
        
        // Cor aleatória
        const color = colors[Math.floor(Math.random() * colors.length)];
        confetti.style.backgroundColor = color;
        
        // Tamanho aleatório
        const size = Math.random() * 10 + 5;
        confetti.style.width = size + 'px';
        confetti.style.height = size + 'px';
        
        // Forma aleatória (quadrado ou círculo)
        if (Math.random() > 0.5) {
            confetti.style.borderRadius = '50%';
        }
        
        // Rotação aleatória
        const rotation = Math.random() * 360;
        confetti.style.transform = `rotate(${rotation}deg)`;
        
        // Adiciona ao container
        container.appendChild(confetti);
        
        // Remove o confete após a animação terminar
        setTimeout(() => {
            confetti.remove();
        }, 3000);
    }
}

// Função para simular a validação do QR Code (para teste)
function simulateQRCodeValidation() {
    // Simula uma localização aleatória para teste
    const locations = [
        'Portão Principal',
        'Entrada VIP',
        'Área Vip',
        'Palco Principal',
        'Área de Alimentação'
    ];
    const randomLocation = locations[Math.floor(Math.random() * locations.length)];
    
    // Mostra a animação de sucesso
    showSuccessAnimation(randomLocation);
}

// Adiciona um evento de clique ao QR Code para teste (apenas em ambiente de desenvolvimento)
document.addEventListener('DOMContentLoaded', function() {
    const qrCodeImage = document.getElementById('qrCodeImage');
    const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    
    if (qrCodeImage && isLocalhost) {
        console.log('Modo de desenvolvimento ativado: Clique no QR Code para testar a animação');
        
        qrCodeImage.addEventListener('click', function() {
            console.log('Teste manual: Iniciando animação de validação...');
            simulateQRCodeValidation();
        });
    }
});

// Função para ser chamada quando o QR Code for validado
const handleQRCodeValidated = function(validationData) {
    console.log('Evento qrCodeValidated recebido com dados:', validationData);
    
    try {
        const location = validationData.detail?.location || validationData.location || 'Ponto de Controle';
        const timestamp = validationData.detail?.timestamp || validationData.timestamp;
        
        console.log('Mostrando animação de sucesso para local:', location);
        
        // Mostra a animação de sucesso
        showSuccessAnimation(location);
        
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
            const now = timestamp ? new Date(timestamp) : new Date();
            const timeString = now.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
            lastUpdated.textContent = `Hoje às ${timeString}`;
            console.log('Horário de atualização definido para:', lastUpdated.textContent);
        }
    } catch (error) {
        console.error('Erro ao processar validação do QR Code:', error);
    }
};

// Registra a função global para ser chamada de outros scripts
window.onQRCodeValidated = handleQRCodeValidated;

// Adiciona um listener de evento para o evento personalizado
document.addEventListener('qrCodeValidated', handleQRCodeValidated);

// Log para confirmar que o script foi carregado
console.log('qr-code-animation.js carregado e aguardando eventos de validação...');
