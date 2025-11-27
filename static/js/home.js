// Aguarda o HTML ser completamente carregado antes de executar o script.
document.addEventListener('DOMContentLoaded', () => {
 
    // =======================================================================
    // === LÓGICA DO MENU LATERAL (MOBILE) ===
    // =======================================================================
    const menuButton = document.getElementById('menu-button');
    const closeButton = document.getElementById('close-button');
    const mobileNav = document.getElementById('mobile-nav');
    const overlay = document.getElementById('overlay');
    
    // Elementos do menu deslizante
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
        // Garante que o menu sempre volte ao painel principal ao ser fechado
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
    if (menuButton) menuButton.addEventListener('click', openMenu);
    if (closeButton) closeButton.addEventListener('click', closeMenu);
    if (overlay) overlay.addEventListener('click', closeMenu);
    
    if (mobileProfileToggle) {
        mobileProfileToggle.addEventListener('click', showProfilePanel);
    }
    
    if (backButton) {
        backButton.addEventListener('click', showMainPanel);
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
    const activateNotificationsBtn = document.getElementById('activate-notifications');

    // Função para mostrar/ocultar a caixa de notificações
    const toggleNotificationDropdown = (event) => {
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
        if (notificationDropdown) {
            notificationDropdown.classList.remove('active');
        }
    };

    // Função para atualizar a interface baseada no estado das notificações
    const updateNotificationUI = (hasNotifications, unreadCount = 0) => {
        const notificationDot = document.querySelector('.notification-dot');
        
        // Mostra/esconde o botão "Marcar todas como lidas"
        if (markAllReadBtn) {
            markAllReadBtn.style.display = hasNotifications && unreadCount > 0 ? 'flex' : 'none';
        }
        
        // Mostra/esconde o ponto de notificação
        if (notificationDot) {
            notificationDot.style.display = unreadCount > 0 ? 'block' : 'none';
        }
    };

    // Função para marcar uma notificação como lida
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
                // Atualiza o contador de notificações não lidas
                const notificationDot = document.querySelector('.notification-dot');
                if (notificationDot) {
                    const unreadCount = parseInt(notificationDot.textContent || '0');
                    if (unreadCount > 0) {
                        notificationDot.textContent = unreadCount - 1;
                        if (unreadCount - 1 === 0) {
                            notificationDot.style.display = 'none';
                        }
                    }
                }
            }
            return data.success;
        } catch (error) {
            console.error('Erro ao marcar notificação como lida:', error);
            return false;
        }
    };

    // Função para marcar todas as notificações como lidas
    const marcarTodasComoLidas = async () => {
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
                // Remove a classe 'unread' de todas as notificações
                document.querySelectorAll('.notification-item.unread').forEach(item => {
                    item.classList.remove('unread');
                });
                
                // Atualiza o contador de notificações não lidas
                const notificationDot = document.querySelector('.notification-dot');
                if (notificationDot) {
                    notificationDot.style.display = 'none';
                }
                
                // Esconde o botão "Marcar todas como lidas"
                if (markAllReadBtn) {
                    markAllReadBtn.style.display = 'none';
                }
            }
            return data.success;
        } catch (error) {
            console.error('Erro ao marcar todas as notificações como lidas:', error);
            return false;
        }
    };

    // Função para mostrar o estado "sem notificações"
    const showNoNotifications = () => {
        if (notificationList) {
            notificationList.innerHTML = `
                <div class="no-notifications">
                    <i class="fa-solid fa-bell-slash"></i>
                    <p>Sem notificações</p>
                </div>
            `;
        }
        
        // Atualiza a UI
        updateNotificationUI(false, 0);
    };

    // Função para obter um cookie pelo nome
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

    // Função para carregar notificações do backend
    const carregarNotificacoes = async () => {
        if (!notificationList) return;
        
        try {
            const response = await fetch('/notificacoes/');
            const data = await response.json();
            
            if (!data || data.total === 0) {
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
                    // Se não tiver evento, adiciona o conteúdo diretamente
                    notificationItem.innerHTML = notificationContent;
                }
                
                // Adiciona evento de clique para mostrar detalhes da notificação
                notificationItem.addEventListener('click', async (e) => {
                    // Previne a navegação se o clique foi em um link
                    if (!e.target.closest('a')) {
                        // Marca como lida se necessário
                        if (!notification.lida) {
                            const success = await marcarNotificacaoComoLida(notification.id, notificationItem);
                            if (success) {
                                notification.lida = true;
                            }
                        }
                        
                        // Abre o modal com os detalhes da notificação
                        if (typeof window.openNotificationModal === 'function') {
                            window.openNotificationModal(notification);
                        }
                        
                        // Fecha o dropdown de notificações
                        closeNotificationDropdown();
                    }
                });
                
                // Adiciona a notificação à lista
                notificationList.appendChild(notificationItem);
            });
            
            // Atualiza a UI
            updateNotificationUI(true, data.nao_lidas || 0);
            
        } catch (error) {
            console.error('Erro ao carregar notificações:', error);
            showNoNotifications();
        }
    };

    // Event listeners para o dropdown de notificações
    if (notificationToggle && notificationDropdown) {
        notificationToggle.addEventListener('click', toggleNotificationDropdown);
        
        // Fechar dropdown ao clicar fora
        document.addEventListener('click', (event) => {
            if (!notificationDropdown.contains(event.target) && !notificationToggle.contains(event.target)) {
                closeNotificationDropdown();
            }
        });
        
        // Evitar que o clique dentro do dropdown feche
        notificationDropdown.addEventListener('click', (event) => {
            event.stopPropagation();
        });
    }

    // Event listener para o botão de marcar todas como lidas
    if (markAllReadBtn) {
        markAllReadBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            e.stopPropagation();
            await marcarTodasComoLidas();
        });
    }

    // Configuração do botão de ativar notificações
    if (activateNotificationsBtn) {
        const setBtnState = (state) => {
            if (!activateNotificationsBtn) return;
            
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

    // Carrega as notificações ao carregar a página
    carregarNotificacoes();

    // =======================================================================
    // === LÓGICA DO FOOTER (APARECE AO ROLAR) ===
    // =======================================================================
    const footer = document.querySelector('.main-footer');
    if (!footer) {
        console.warn('Footer não encontrado');
        return;
    }
    
    let lastScrollY = window.scrollY;
    let scrollThreshold = 50; // Reduzido para ativar mais cedo
    let hideTimeout;
    let isVisible = false;

    // Função para mostrar/esconder o footer baseado no scroll
    const handleFooterVisibility = () => {
        const currentScrollY = window.scrollY;
        const windowHeight = window.innerHeight;
        const documentHeight = document.documentElement.scrollHeight;
        
        // Debug: log para verificar valores
        console.log('Scroll:', currentScrollY, 'Window Height:', windowHeight, 'Doc Height:', documentHeight);
        
        // Mostra o footer se rolar para baixo além do threshold
        if (currentScrollY > scrollThreshold) {
            if (!isVisible) {
                footer.classList.add('visible');
                isVisible = true;
                console.log('Footer visível - scroll > threshold');
            }
            clearTimeout(hideTimeout);
            
            // Esconde o footer após parar de rolar por 4 segundos
            hideTimeout = setTimeout(() => {
                // Verifica se ainda não está no topo
                if (window.scrollY > scrollThreshold) {
                    footer.classList.remove('visible');
                    isVisible = false;
                    console.log('Footer escondido por timeout');
                }
            }, 4000);
        } else {
            // Esconde se estiver no topo da página
            if (isVisible) {
                footer.classList.remove('visible');
                isVisible = false;
                console.log('Footer escondido - topo da página');
            }
            clearTimeout(hideTimeout);
        }
        
        // Mostra o footer permanentemente quando estiver próximo ao final
        const scrollPosition = currentScrollY + windowHeight;
        if (scrollPosition >= documentHeight - 150) {
            if (!isVisible) {
                footer.classList.add('visible');
                isVisible = true;
                clearTimeout(hideTimeout);
                console.log('Footer visível - final da página');
            }
        }
        
        lastScrollY = currentScrollY;
    };

    // Adiciona o evento de scroll com throttle para performance
    let ticking = false;
    const scrollHandler = () => {
        if (!ticking) {
            requestAnimationFrame(() => {
                handleFooterVisibility();
                ticking = false;
            });
            ticking = true;
        }
    };

    // Adiciona o evento de scroll
    window.addEventListener('scroll', scrollHandler, { passive: true });

    // Verifica inicialmente se a página já tem scroll suficiente
    setTimeout(() => {
        handleFooterVisibility();
    }, 100);

    // Verifica também quando a página é redimensionada
    window.addEventListener('resize', () => {
        setTimeout(() => {
            handleFooterVisibility();
        }, 100);
    }, { passive: true });
});