document.addEventListener('DOMContentLoaded', function() {
    // Elementos do modal de notificação
    const notificationModal = document.getElementById('notification-modal');
    const notificationModalOverlay = document.getElementById('notification-modal-overlay');
    const notificationModalClose = document.getElementById('notification-modal-close');
    
    // Função para abrir o modal de notificação
    window.openNotificationModal = function(notification) {
        const modalTitle = document.getElementById('notification-modal-title');
        const modalMessage = document.getElementById('notification-modal-message');
        const modalTime = document.getElementById('notification-modal-time');
        const modalIcon = document.getElementById('notification-modal-icon');
        const modalActions = document.getElementById('notification-modal-actions');
        
        // Mapeamento de ícones por tipo
        const iconMap = {
            'info': 'fa-info-circle',
            'success': 'fa-check-circle',
            'warning': 'fa-exclamation-triangle',
            'error': 'fa-exclamation-circle'
        };
        
        // Atualiza o conteúdo do modal
        modalTitle.textContent = notification.titulo;
        modalMessage.textContent = notification.mensagem;
        modalTime.textContent = notification.tempo || 'Agora mesmo';
        
        // Atualiza o ícone baseado no tipo
        const iconClass = iconMap[notification.tipo] || 'fa-info-circle';
        modalIcon.className = `notification-modal-icon ${notification.tipo}`;
        modalIcon.innerHTML = `<i class="fa-solid ${iconClass}"></i>`;
        
        // Limpa ações anteriores
        modalActions.innerHTML = '';
        
        // Adiciona botão de ação se houver um link
        if (notification.link) {
            const linkBtn = document.createElement('a');
            linkBtn.className = 'btn btn-primary';
            linkBtn.textContent = 'Ver detalhes';
            linkBtn.href = notification.link;
            modalActions.appendChild(linkBtn);
        }
        
        // Botão para fechar
        const closeBtn = document.createElement('button');
        closeBtn.className = 'btn btn-outline';
        closeBtn.textContent = 'Fechar';
        closeBtn.onclick = closeNotificationModal;
        modalActions.appendChild(closeBtn);
        
        // Mostra o modal
        notificationModal.classList.add('active');
        document.body.style.overflow = 'hidden'; // Impede rolagem da página
        
        // Marca a notificação como lida se necessário
        if (!notification.lida && notification.id) {
            markNotificationAsRead(notification.id);
        }
    };
    
    // Função para marcar notificação como lida
    function markNotificationAsRead(notificationId) {
        fetch(`/notificacoes/${notificationId}/marcar-lida/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
            }
        });
    }
    
    // Função para fechar o modal de notificação
    function closeNotificationModal() {
        notificationModal.classList.remove('active');
        document.body.style.overflow = ''; // Restaura rolagem da página
    }
    
    // Event listeners para o modal
    if (notificationModalOverlay) {
        notificationModalOverlay.addEventListener('click', closeNotificationModal);
    }
    
    if (notificationModalClose) {
        notificationModalClose.addEventListener('click', closeNotificationModal);
    }
    
    // Fecha o modal ao pressionar ESC
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && notificationModal.classList.contains('active')) {
            closeNotificationModal();
        }
    });
    
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
});
