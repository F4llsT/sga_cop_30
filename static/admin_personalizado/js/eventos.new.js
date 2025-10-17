// Função para controlar a visibilidade do modal
function toggleModal(show = true) {
    const modal = document.getElementById('confirm-modal');
    if (!modal) return;

    if (show) {
        // Previne rolagem da página quando o modal está aberto
        document.body.style.overflow = 'hidden';
        // Mostra o modal
        modal.style.display = 'flex';
        // Força um reflow para permitir a transição
        void modal.offsetWidth;
        // Adiciona a classe show para ativar a transição
        modal.classList.add('show');
    } else {
        // Remove a classe show para iniciar a transição de saída
        modal.classList.remove('show');
        // Habilita a rolagem da página
        document.body.style.overflow = '';
        // Esconde o modal após a transição
        setTimeout(() => {
            if (!modal.classList.contains('show')) {
                modal.style.display = 'none';
            }
        }, 300);
    }
}

// Adiciona efeito de ripple nos botões
function addRippleEffect(button) {
    button.addEventListener('click', function(e) {
        // Verifica se o botão já tem um ripple
        if (this.querySelector('.ripple')) return;
        
        const rect = this.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        const ripple = document.createElement('span');
        ripple.className = 'ripple';
        ripple.style.left = `${x}px`;
        ripple.style.top = `${y}px`;
        
        this.appendChild(ripple);
        
        // Remove o efeito após a animação
        setTimeout(() => {
            ripple.remove();
        }, 600);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    // Elementos do DOM
    const formEvento = document.querySelector('#form-evento');
    const listaEventos = document.getElementById('lista-eventos');
    const eventoIdInput = document.getElementById('evento-id');
    const searchInput = document.getElementById('search-input');
    
    // Verifica se os elementos necessários existem
    if (!formEvento || !listaEventos) {
        console.error('Elementos necessários não encontrados');
        return;
    }
    
    // URLs da API
    const API_BASE = '/meu-admin';
    const API_URL = `${API_BASE}/eventos/`;
    const API_EVENTOS = `${API_BASE}/api/eventos/`;
    
    // Estado da aplicação
    let eventos = [];
    let editMode = false;
    let eventoParaExcluir = null;
    
    // Obtém o token CSRF
    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]')?.value;
    if (!csrfToken) {
        console.error('Token CSRF não encontrado');
        showAlert('Erro de segurança. Por favor, recarregue a página.', 'error');
        return;
    }
    
    // Inicialização
    initEventListeners();
    carregarEventos();
    atualizarContadores();
    
    /**
     * Inicializa os event listeners
     */
    function initEventListeners() {
        // Formulário de evento
        formEvento.addEventListener('submit', handleFormSubmit);
        
        // Botão de limpar formulário
        const btnLimpar = document.getElementById('btn-limpar');
        if (btnLimpar) {
            btnLimpar.addEventListener('click', resetarFormulario);
            addRippleEffect(btnLimpar);
        }
        
        // Botão de atualizar
        const btnAtualizar = document.getElementById('btn-atualizar');
        if (btnAtualizar) {
            btnAtualizar.addEventListener('click', async () => {
                btnAtualizar.classList.add('rotating');
                await Promise.all([carregarEventos(), atualizarContadores()]);
                setTimeout(() => btnAtualizar.classList.remove('rotating'), 500);
            });
            addRippleEffect(btnAtualizar);
        }
        
        // Barra de pesquisa
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                pesquisarEventos(e.target.value.trim());
            });
        }
        
        // Filtro de status
        const filterStatus = document.getElementById('filter-status');
        if (filterStatus) {
            filterStatus.addEventListener('change', (e) => {
                filtrarEventosPorStatus(e.target.value);
            });
        }
        
        // Fechar modal ao clicar fora
        document.addEventListener('click', (e) => {
            const modal = document.getElementById('confirm-modal');
            if (e.target === modal) {
                toggleModal(false);
            }
        });
        
        // Fechar modal com tecla Escape
        document.addEventListener('keydown', (e) => {
            const modal = document.getElementById('confirm-modal');
            if (e.key === 'Escape' && modal && modal.style.display === 'flex') {
                toggleModal(false);
            }
        });
        
        // Botões de fechar modal
        document.querySelectorAll('.close-modal, [data-dismiss="modal"]').forEach(btn => {
            btn.addEventListener('click', () => toggleModal(false));
            addRippleEffect(btn);
        });
        
        // Botão de confirmar exclusão
        const btnConfirmar = document.getElementById('btn-confirmar-exclusao');
        if (btnConfirmar) {
            btnConfirmar.addEventListener('click', handleConfirmarExclusao);
            addRippleEffect(btnConfirmar);
        }
        
        // Adiciona efeito de ripple em todos os botões
        document.querySelectorAll('.btn').forEach(btn => {
            addRippleEffect(btn);
        });
    }
    
    /**
     * Manipula a confirmação de exclusão
     */
    function handleConfirmarExclusao() {
        if (!eventoParaExcluir) return;
        
        // Aqui você deve adicionar a lógica para excluir o evento
        console.log('Excluindo evento:', eventoParaExcluir);
        
        // Fecha o modal após a exclusão
        toggleModal(false);
        
        // Limpa a referência ao evento
        eventoParaExcluir = null;
    }
    
    // Função para preparar a exclusão de um evento
    function prepararExclusao(evento) {
        eventoParaExcluir = evento;
        toggleModal(true);
    }
    
    // ... (restante do seu código existente)
    
    // Atualiza a função que cria os cards de evento para usar o novo sistema de exclusão
    function criarCardEvento(evento) {
        // ... (código existente)
        
        // Substitua a chamada direta de exclusão por:
        // btnExcluir.addEventListener('click', () => prepararExclusao(evento));
        
        // ... (restante do código existente)
    }
    
    // Inicializa o modal como oculto
    const modal = document.getElementById('confirm-modal');
    if (modal) {
        modal.style.display = 'none';
    }
});

// Adiciona estilos para o efeito ripple
const rippleStyle = document.createElement('style');
rippleStyle.textContent = `
    .btn {
        position: relative;
        overflow: hidden;
    }
    .btn .ripple {
        position: absolute;
        border-radius: 50%;
        background-color: rgba(255, 255, 255, 0.7);
        transform: scale(0);
        animation: ripple 0.6s linear;
        pointer-events: none;
    }
    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
`;
document.head.appendChild(rippleStyle);
