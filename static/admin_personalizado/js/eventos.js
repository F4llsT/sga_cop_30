document.addEventListener('DOMContentLoaded', () => {
    const formEvento = document.getElementById('form-evento');
    const listaEventos = document.getElementById('lista-eventos');
    const formTitle = document.getElementById('form-title');
    const eventoIdInput = document.getElementById('evento-id');

    // Simulação de banco de dados
    let eventos = [];
    let eventIdCounter = 0;
    let editMode = false;

    const renderizarEventos = () => {
        listaEventos.innerHTML = '';
        if (eventos.length === 0) {
            listaEventos.innerHTML = '<p class="empty-state">Nenhum evento agendado no momento.</p>';
            return;
        }
        eventos.forEach(evento => listaEventos.appendChild(criarCardEvento(evento)));
    };

    const criarCardEvento = (evento) => {
        const card = document.createElement('div');
        card.className = `event-card ${evento.importante ? 'importante' : ''}`;
        card.dataset.id = evento.id;
        card.innerHTML = `
            <div class="event-details">
                <h4>${evento.titulo}</h4>
                <p>${evento.descricao}</p>
                <div class="event-meta">
                    <span><i class="fa-solid fa-calendar-day"></i> ${evento.data}</span>
                    <span><i class="fa-solid fa-clock"></i> ${evento.inicio} - ${evento.fim}</span>
                    <span><i class="fa-solid fa-location-dot"></i> ${evento.local}</span>
                </div>
            </div>
            <div class="event-actions">
                <button class="edit-btn" title="Editar"><i class="fa-solid fa-pencil"></i></button>
                <button class="delete-btn" title="Remover"><i class="fa-solid fa-trash"></i></button>
            </div>
        `;
        return card;
    };

    const resetarFormulario = () => {
        formEvento.reset();
        eventoIdInput.value = '';
        formTitle.textContent = 'Criar Novo Evento';
        formEvento.querySelector('.btn-salvar').textContent = 'Salvar Evento';
        editMode = false;
    };

    formEvento.addEventListener('submit', (e) => {
        e.preventDefault();

        const id = eventoIdInput.value;
        const eventoData = {
            titulo: document.getElementById('evento-titulo').value,
            descricao: document.getElementById('evento-descricao').value,
            data: document.getElementById('evento-data').value,
            inicio: document.getElementById('evento-inicio').value,
            fim: document.getElementById('evento-fim').value,
            local: document.getElementById('evento-local').value,
            tema: document.getElementById('evento-tema').value,
            importante: document.getElementById('evento-importante').checked,
        };

        if (editMode && id) {
            // Modo Edição
            const index = eventos.findIndex(evento => evento.id == id);
            if (index !== -1) {
                eventos[index] = { ...eventos[index], ...eventoData };
                alert('Evento atualizado com sucesso!');
            }
        } else {
            // Modo Criação
            eventos.unshift({ id: eventIdCounter++, ...eventoData });
        }
        
        resetarFormulario();
        renderizarEventos();
    });

    listaEventos.addEventListener('click', (e) => {
        const target = e.target.closest('button');
        if (!target) return;

        const card = target.closest('.event-card');
        const id = parseInt(card.dataset.id);

        if (target.classList.contains('delete-btn')) {
            if (confirm('Tem certeza que deseja excluir este evento?')) {
                eventos = eventos.filter(evento => evento.id !== id);
                renderizarEventos();
            }
        }

        if (target.classList.contains('edit-btn')) {
            const evento = eventos.find(evento => evento.id === id);
            if (evento) {
                formTitle.textContent = 'Editar Evento';
                formEvento.querySelector('.btn-salvar').textContent = 'Salvar Alterações';
                editMode = true;

                document.getElementById('evento-id').value = evento.id;
                document.getElementById('evento-titulo').value = evento.titulo;
                document.getElementById('evento-descricao').value = evento.descricao;
                document.getElementById('evento-data').value = evento.data;
                document.getElementById('evento-inicio').value = evento.inicio;
                document.getElementById('evento-fim').value = evento.fim;
                document.getElementById('evento-local').value = evento.local;
                document.getElementById('evento-tema').value = evento.tema;
                document.getElementById('evento-importante').checked = evento.importante;

                formEvento.scrollIntoView({ behavior: 'smooth' });
            }
        }
    });

    renderizarEventos();
});