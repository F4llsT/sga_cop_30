document.addEventListener('DOMContentLoaded', () => {
    
    // =======================================================================
    // === LÓGICA DO MENU LATERAL (MOBILE) ===
    // =======================================================================
    const menuButton = document.getElementById('admin-menu-button');
    const closeButton = document.getElementById('admin-close-button');
    const mobileNav = document.getElementById('admin-mobile-nav');
    const overlay = document.getElementById('admin-overlay');

    if (menuButton && closeButton && mobileNav && overlay) {
        const openMenu = () => {
            mobileNav.classList.add('active');
            overlay.classList.add('active');
        };

        const closeMenu = () => {
            mobileNav.classList.remove('active');
            overlay.classList.remove('active');
        };
        menuButton.addEventListener('click', openMenu);
        closeButton.addEventListener('click', closeMenu);
        overlay.addEventListener('click', closeMenu);
    }

    // =======================================================================
    // === ANIMAÇÃO DAS LOGOS (DESKTOP E MOBILE) ===
    // =======================================================================
    
    // Função genérica para animar qualquer logo que siga a estrutura
    const setupLogoAnimation = (logoElement) => {
        if (!logoElement) return;

        const planetIcon = logoElement.querySelector('.planet-icon');
        const letters = logoElement.querySelectorAll('.letter');
        let isAnimating = false;

        const playAnimation = () => {
            if (isAnimating || !letters.length) return;
            isAnimating = true;
            logoElement.classList.add('animating');

            setTimeout(() => {
                logoElement.classList.remove('animating');
                isAnimating = false;
            }, 2000);
        };

        logoElement.addEventListener('mouseover', playAnimation);
    };

    // Seleciona as duas logos pelos seus IDs
    const mainLogo = document.getElementById('admin-main-logo');
    const sidebarLogo = document.getElementById('admin-sidebar-logo');
    
    // Aplica a funcionalidade de animação para ambas
    setupLogoAnimation(mainLogo);
    setupLogoAnimation(sidebarLogo);

    // =======================================================================
    // === LÓGICA DOS GRÁFICOS RESPONSIVOS ===
    // =======================================================================

    // REGISTRA O PLUGIN DE RÓTULOS (DATALABELS)
    if (typeof ChartDataLabels !== 'undefined') {
        Chart.register(ChartDataLabels);
    }

    const eventosCanvas = document.getElementById('eventosChart');
    const passeFacilCanvas = document.getElementById('passeFacilChart');

    let eventosChartInstance = null;
    let passeFacilChartInstance = null;

    const renderCharts = () => {
        if (eventosChartInstance) eventosChartInstance.destroy();
        if (passeFacilChartInstance) passeFacilChartInstance.destroy();

        const isMobile = window.innerWidth < 768;

        // --- Gráfico 1: Eventos Mais Favoritados ---
        if (eventosCanvas) {
            const eventosCtx = eventosCanvas.getContext('2d');
            eventosChartInstance = new Chart(eventosCtx, {
                type: 'bar',
                data: {
                    labels: ['Painel Amazônia', 'Workshop E.', 'Reunião Delegação', 'Cúpula de E.R.'],
                    datasets: [{
                        label: 'Nº de Favoritos',
                        data: [280, 195, 150, 120],
                        backgroundColor: [
                            'rgba(139, 92, 246, 0.7)',
                            'rgba(139, 92, 246, 0.7)',
                            'rgba(139, 92, 246, 0.7)',
                            'rgba(139, 92, 246, 0.7)'
                        ],
                        borderColor: 'rgba(139, 92, 246, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    indexAxis: isMobile ? 'x' : 'y',
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        datalabels: { display: false }
                    },
                    scales: {
                        x: {
                            ticks: {
                                autoSkip: false,
                                maxRotation: isMobile ? 45 : 0,
                                minRotation: isMobile ? 45 : 0
                            }
                        }
                    }
                }
            });
        }

        // --- Gráfico 2: Uso do Passe Fácil ---
        if (passeFacilCanvas) {
            const passeFacilCtx = passeFacilCanvas.getContext('2d');
            const passeFacilData = [450, 329, 100];
            const totalPasseFacil = passeFacilData.reduce((sum, value) => sum + value, 0);

            passeFacilChartInstance = new Chart(passeFacilCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Estudante', 'Profissional', 'Imprensa'],
                    datasets: [{
                        label: 'Usos',
                        data: passeFacilData,
                        backgroundColor: ['rgb(34, 197, 94)', 'rgb(59, 130, 246)', 'rgb(245, 158, 11)'],
                        hoverOffset: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: isMobile ? 'bottom' : 'top',
                        },
                        datalabels: {
                            display: isMobile,
                            formatter: (value, context) => {
                                const percentage = ((value / totalPasseFacil) * 100).toFixed(1) + '%';
                                return value + '\n' + `(${percentage})`;
                            },
                            color: '#fff',
                            textAlign: 'center',
                            font: { weight: 'bold', size: 12 }
                        }
                    }
                }
            });
        }
    };

    renderCharts();
    let resizeTimer;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(renderCharts, 250);
    });
});