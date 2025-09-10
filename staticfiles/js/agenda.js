// agenda.js (código completo)
document.addEventListener('DOMContentLoaded', () => {
    const filterForm = document.getElementById('filter-form');
    const agendaList = document.querySelector('.agenda-list');
    
    // Este código garante que os selects mantenham o valor selecionado após o filtro
    const urlParams = new URLSearchParams(window.location.search);
    const dayFilter = urlParams.get('day');
    const themeFilter = urlParams.get('theme');

    if (dayFilter) {
        document.getElementById('filter-day').value = dayFilter;
    }
    if (themeFilter) {
        document.getElementById('filter-theme').value = themeFilter;
    }

    // Ação do formulário (opcional, se você quiser um carregamento dinâmico)
    if (filterForm) {
        filterForm.addEventListener('submit', () => {
            agendaList.innerHTML = '<p class="loading-message">Carregando eventos...</p>';
        });
    }
});