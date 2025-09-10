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
});