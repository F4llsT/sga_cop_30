// Aguarda o HTML ser completamente carregado antes de executar o script.



document.addEventListener('DOMContentLoaded', () => {
 
    
    // =======================================================================
    // === LÓGICA DO MENU LATERAL (MOBILE) - CORRIGIDA ===
    // =======================================================================
    const menuButton = document.getElementById('menu-button');
    const closeButton = document.getElementById('close-button');
    const mobileNav = document.getElementById('mobile-nav');
    const overlay = document.getElementById('overlay');
    
    // Elementos do novo menu deslizante
    const mobileNavSlider = document.getElementById('mobile-nav-slider');
    const mobileProfileToggle = document.getElementById('mobile-profile-toggle');
    const backButton = document.getElementById('back-to-main-menu');

    // Funções para abrir/fechar o menu principal
    const openMenu = () => {
        mobileNav.classList.add('active');
        overlay.classList.add('active');
    };
    const closeMenu = () => {
        mobileNav.classList.remove('active');
        overlay.classList.remove('active');
        // Importante: Garante que o menu sempre volte ao painel principal ao ser fechado
        if (mobileNavSlider) {
            mobileNavSlider.classList.remove('show-profile');
        }
    };

    // Funções para deslizar entre os painéis
    const showProfilePanel = () => {
        if (mobileNavSlider) {
            mobileNavSlider.classList.add('show-profile');
        }
    };
    const showMainPanel = () => {
        if (mobileNavSlider) {
            mobileNavSlider.classList.remove('show-profile');
        }
    };

    // Adiciona os "escutadores" de eventos
    menuButton.addEventListener('click', openMenu);
    closeButton.addEventListener('click', closeMenu);
    overlay.addEventListener('click', closeMenu);
    
    if (mobileProfileToggle) {
        mobileProfileToggle.addEventListener('click', showProfilePanel); // Ao clicar em "Visitante", mostra o painel do perfil
    }
    if (backButton) {
        backButton.addEventListener('click', showMainPanel); // Ao clicar em "Voltar", mostra o painel principal
    }


    // =======================================================================
    // === LÓGICA DA ANIMAÇÃO DO SINO ===
    // =======================================================================
    const notificationBell = document.querySelector('.notification-bell');
    let isBellAnimating = false;
    if (notificationBell) {
        notificationBell.addEventListener('mouseover', () => {
            if (!isBellAnimating) {
                isBellAnimating = true;
                notificationBell.classList.add('is-swinging');
            }
        });
        notificationBell.addEventListener('animationend', () => {
            notificationBell.classList.remove('is-swinging');
            isBellAnimating = false;
        });
    }

    // =======================================================================
    // === ANIMAÇÃO DA LOGO ===
    // =======================================================================
    const mainLogo = document.getElementById('main-logo');
    if (mainLogo) {
        const planetIcon = mainLogo.querySelector('.planet-icon');
        const letters = mainLogo.querySelectorAll('.letter');
        let isLogoAnimating = false;

        const playLogoAnimation = () => {
            if (isLogoAnimating) return;
            isLogoAnimating = true;

            planetIcon.style.animation = 'planet-eat 1.5s ease-in-out forwards';

            letters.forEach((letter, index) => {
                setTimeout(() => {
                    letter.style.transform = 'scale(0)';
                    letter.style.opacity = '0';
                }, index * 80);
            });

            setTimeout(() => {
                letters.forEach((letter, index) => {
                    setTimeout(() => {
                        letter.style.transition = 'transform 0.4s cubic-bezier(0.68, -0.55, 0.27, 1.55), opacity 0.3s ease-out';
                        letter.style.transform = 'scale(1)';
                        letter.style.opacity = '1';
                    }, index * 80);
                });
            }, 1600);

            setTimeout(() => {
                planetIcon.style.animation = 'none';
                letters.forEach(letter => letter.style.transition = 'all 0.2s ease-out');
                isLogoAnimating = false;
            }, 2500);
        };

        mainLogo.addEventListener('mouseover', playLogoAnimation);
    }

    // =======================================================================
    // === LÓGICA DO DROPDOWN DO PERFIL (DESKTOP) ===
    // =======================================================================
    const profileToggle = document.getElementById('profile-toggle');
    const profileDropdown = document.getElementById('profile-dropdown');

    if (profileToggle && profileDropdown) {
        profileToggle.addEventListener('click', (event) => {
            event.stopPropagation();
            profileDropdown.classList.toggle('active');
            profileToggle.classList.toggle('active');
        });

        window.addEventListener('click', () => {
            if (profileDropdown.classList.contains('active')) {
                profileDropdown.classList.remove('active');
                profileToggle.classList.remove('active');
            }
        });
    }

    // =======================================================================
    // === LÓGICA DA CAIXA DE NOTIFICAÇÕES ===
    // =======================================================================
    const notificationToggle = document.getElementById('notification-toggle');
    const notificationDropdown = document.getElementById('notification-dropdown');
    const notificationList = document.getElementById('notification-list');
    const markAllReadBtn = document.getElementById('mark-all-read');

    // Função para mostrar/ocultar a caixa de notificações
    const toggleNotificationDropdown = (event) => {
        console.log('Toggle notification dropdown clicked!');
        event.preventDefault();
        event.stopPropagation();
        
        // Fecha o dropdown do perfil se estiver aberto
        if (profileDropdown && profileDropdown.classList.contains('active')) {
            profileDropdown.classList.remove('active');
            profileToggle.classList.remove('active');
        }
        
        // Toggle do dropdown de notificações
        notificationDropdown.classList.toggle('active');
    };

    // Função para fechar a caixa de notificações
    const closeNotificationDropdown = () => {
        notificationDropdown.classList.remove('active');
    };

    // Função para atualizar a interface baseada no estado das notificações
    const updateNotificationUI = (hasNotifications, unreadCount = 0) => {
        const markAllReadBtn = document.getElementById('mark-all-read');
        const notificationDot = document.querySelector('.notification-dot');
        
        // Mostra/esconde o botão "Marcar todas como lidas"
        if (markAllReadBtn) {
            markAllReadBtn.style.display = hasNotifications && unreadCount > 0 ? 'block' : 'none';
        }
        
        // Mostra/esconde o ponto de notificação
        if (notificationDot) {
            notificationDot.style.display = unreadCount > 0 ? 'block' : 'none';
        }
    };

    // Função para carregar notificações do backend
    const carregarNotificacoes = async () => {
        try {
            const response = await fetch('/notificacoes/');
            const data = await response.json();
            
            if (data.total === 0) {
                showNoNotifications();
                return;
            }
            
            // Remove o estado "sem notificações"
            const noNotifications = notificationList.querySelector('.no-notifications');
            if (noNotifications) {
                noNotifications.remove();
            }
            
            // Limpa a lista atual
            notificationList.innerHTML = '';
            
            // Adiciona as notificações do backend
            data.notificacoes.forEach(notification => {
                const notificationItem = document.createElement('div');
                notificationItem.className = `notification-item ${!notification.lida ? 'unread' : ''}`;
                notificationItem.dataset.notificationId = notification.id;
                
                const iconMap = {
                    'info': 'fa-info-circle',
                    'success': 'fa-check-circle',
                    'warning': 'fa-exclamation-triangle',
                    'error': 'fa-exclamation-circle'
                };
                
                // Verifica se a notificação está vinculada a um evento
                const hasEvent = notification.evento_id !== null && notification.evento_id !== undefined;
                const notificationContent = `
                    <div class="notification-icon ${notification.tipo}">
                        <i class="fa-solid ${iconMap[notification.tipo] || 'fa-info-circle'}"></i>
                    </div>
                    <div class="notification-content">
                        <h4 class="notification-title">${notification.titulo}</h4>
                        <p class="notification-message">${notification.mensagem}</p>
                        <p class="notification-time">${notification.tempo}</p>
                    </div>
                `;
                
                if (hasEvent) {
                    // Se tiver evento, cria um link para a página do evento
                    const notificationLink = document.createElement('a');
                    notificationLink.href = `/agenda/evento/${notification.evento_id}/`;
                    notificationLink.className = 'notification-link';
                    notificationLink.innerHTML = notificationContent;
                    notificationItem.appendChild(notificationLink);
                    
                    // Adiciona classe para indicar que é clicável
                    notificationItem.classList.add('has-event');
                } else {
                    // Se não tiver evento, mantém o conteúdo normal
                    notificationItem.innerHTML = notificationContent;
                }
                
                // Adiciona evento de clique para marcar como lida
                notificationItem.addEventListener('click', (e) => {
                    // Previne a navegação se o clique foi em um link
                    if (!e.target.closest('a')) {
                        if (!notification.lida) {
                            marcarNotificacaoComoLida(notification.id, notificationItem);
                        }
                    }
                });
                
                notificationList.appendChild(notificationItem);
            });
            
            // Atualiza a UI
            updateNotificationUI(true, data.nao_lidas);
            
        } catch (error) {
            console.error('Erro ao carregar notificações:', error);
            showNoNotifications();
        }
    };

    // Função para marcar uma notificação específica como lida
    const marcarNotificacaoComoLida = async (notificationId, element) => {
        try {
            const response = await fetch(`/notificacoes/${notificationId}/marcar-lida/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json',
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                element.classList.remove('unread');
                // Recarrega as notificações para atualizar contadores
                carregarNotificacoes();
            }
        } catch (error) {
            console.error('Erro ao marcar notificação como lida:', error);
        }
    };

    // Função para obter CSRF token
    const getCookie = (name) => {
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
    };

    // Função para mostrar estado "sem notificações"
    const showNoNotifications = () => {
        notificationList.innerHTML = `
            <div class="no-notifications">
                <i class="fa-solid fa-bell-slash"></i>
                <p>Sem notificações</p>
            </div>
        `;
        updateNotificationUI(false, 0);
    };

    // Função para marcar todas como lidas
    const markAllAsRead = async () => {
        try {
            const response = await fetch('/notificacoes/marcar-todas-lidas/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json',
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Recarrega as notificações para atualizar a UI
                carregarNotificacoes();
            } else {
                console.error('Erro ao marcar notificações como lidas:', data.message);
            }
        } catch (error) {
            console.error('Erro ao marcar notificações como lidas:', error);
        }
    };

    // Event listeners
    console.log('Notification toggle element:', notificationToggle);
    console.log('Notification dropdown element:', notificationDropdown);
    
    // Teste adicional
    if (notificationToggle) {
        console.log('Notification toggle found, adding click listener');
        notificationToggle.addEventListener('click', (e) => {
            console.log('Click event fired on notification toggle');
            toggleNotificationDropdown(e);
        });
    } else {
        console.error('Notification toggle element not found!');
    }
    
    if (notificationDropdown) {
        console.log('Notification dropdown found');
    } else {
        console.error('Notification dropdown element not found!');
    }
    
    // Fecha quando clica fora
    if (notificationDropdown && notificationToggle) {
        window.addEventListener('click', (event) => {
            if (!notificationDropdown.contains(event.target) && !notificationToggle.contains(event.target)) {
                closeNotificationDropdown();
            }
        });
    }

    if (markAllReadBtn) {
        markAllReadBtn.addEventListener('click', markAllAsRead);
    }

    // Carrega notificações do backend ao inicializar
    carregarNotificacoes();

    // =======================================================================
    // OneSignal: Ativar notificações sob demanda (ao clicar no botão)
    // =======================================================================
    const activateNotificationsBtn = document.getElementById('activate-notifications');
    if (activateNotificationsBtn) {
        const setBtnState = (state) => {
            if (state === 'granted') {
                activateNotificationsBtn.textContent = 'Notificações ativadas';
                activateNotificationsBtn.disabled = true;
                activateNotificationsBtn.classList.add('is-active');
            } else if (state === 'denied') {
                activateNotificationsBtn.textContent = 'Permissão negada (ajuste no navegador)';
                activateNotificationsBtn.disabled = true;
                activateNotificationsBtn.classList.add('is-denied');
            } else {
                activateNotificationsBtn.textContent = 'Ativar notificações';
                activateNotificationsBtn.disabled = false;
                activateNotificationsBtn.classList.remove('is-active', 'is-denied');
            }
        };

        // Tenta detectar o status atual e ajustar o botão
        if ('Notification' in window) {
            try {
                setBtnState(Notification.permission);
            } catch (_) {}
        }

        activateNotificationsBtn.addEventListener('click', () => {
            if (!window.OneSignalDeferred) {
                console.warn('OneSignal SDK ainda não carregou.');
                return;
            }
            window.OneSignalDeferred.push(function(OneSignal) {
                // Se já está concedido, apenas confirma estado
                OneSignal.Notifications.getPermissionStatus().then((status) => {
                    if (status === 'granted') {
                        setBtnState('granted');
                        return;
                    }
                    // Solicita permissão ao usuário
                    OneSignal.Notifications.requestPermission().then((result) => {
                        // result: 'granted' | 'denied' | 'default'
                        setBtnState(result);
                    }).catch((err) => {
                        console.error('Erro ao solicitar permissão de notificação:', err);
                    });
                });
            });
        });
    }
});