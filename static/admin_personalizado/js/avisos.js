document.addEventListener('DOMContentLoaded', () => {
    const formAviso = document.getElementById('form-aviso');
    const listaAvisosAtivos = document.getElementById('lista-avisos-ativos');
    const listaHistorico = document.getElementById('lista-historico');
    const selectImportancia = document.getElementById('aviso-importancia');

    // --- FUNÇÕES DE RENDERIZAÇÃO ---
    const renderizarAvisos = (avisosAtivos, avisosHistorico) => {
        // Renderizar avisos ativos
        listaAvisosAtivos.innerHTML = '';
        if (avisosAtivos.length === 0) {
            listaAvisosAtivos.innerHTML = '<p class="empty-state">Nenhum aviso ativo no momento.</p>';
        } else {
            avisosAtivos.forEach(aviso => {
                listaAvisosAtivos.appendChild(criarCardAviso(aviso));
            });
        }

        // Renderizar histórico
        listaHistorico.innerHTML = '';
        if (avisosHistorico.length === 0) {
            listaHistorico.innerHTML = '<p class="empty-state">Nenhum aviso no histórico.</p>';
        } else {
            avisosHistorico.forEach(aviso => {
                listaHistorico.appendChild(criarItemHistorico(aviso));
            });
        }
    };

    // --- FUNÇÕES DE CRIAÇÃO DE ELEMENTOS ---
    const criarCardAviso = (aviso) => {
        const card = document.createElement('div');
        card.className = `notice-card ${aviso.nivel}`;
        card.dataset.id = aviso.id;
        
        const dataExpiracao = aviso.data_expiracao ? 
            new Date(aviso.data_expiracao).toLocaleString('pt-BR') : 
            'Não expira';
        
        card.innerHTML = `
            <div class="notice-content">
                <h4>${aviso.titulo}</h4>
                <p>${aviso.mensagem}</p>
                <span class="notice-info">Expira em: ${dataExpiracao}</span>
            </div>
            <div class="notice-actions">
                <button class="pin-btn ${aviso.fixo_no_topo ? 'pinned' : ''}" 
                        title="Fixar no topo" 
                        data-id="${aviso.id}">
                    <i class="fa-solid fa-thumbtack"></i>
                </button>
                <button class="delete-btn" title="Remover" data-id="${aviso.id}">
                    <i class="fa-solid fa-trash"></i>
                </button>
            </div>
        `;
        return card;
    };

    const criarItemHistorico = (aviso) => {
        const item = document.createElement('div');
        item.className = 'history-item';
        
        const dataExpiracao = aviso.data_expiracao ? 
            new Date(aviso.data_expiracao).toLocaleDateString('pt-BR') : 
            'Desativado manualmente';
        
        item.innerHTML = `
            <span><strong>${aviso.titulo}</strong> - <em>${aviso.mensagem}</em></span>
            <span class="notice-info">Expirou em: ${dataExpiracao}</span>
        `;
        return item;
    };

    // --- FUNÇÃO PARA OBTER CSRF TOKEN ---
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

    const csrftoken = getCookie('csrftoken');

    // --- FUNÇÃO PARA CARREGAR AVISOS VIA API ---
    const carregarAvisos = async () => {
        try {
            const response = await fetch('/admin_personalizado/api/avisos/');
            const data = await response.json();
            
            if (data.success) {
                renderizarAvisos(data.avisos_ativos, data.avisos_historico);
            }
        } catch (error) {
            console.error('Erro ao carregar avisos:', error);
        }
    };

    // --- EVENT LISTENER DO FORMULÁRIO ---
    if (formAviso) {
        formAviso.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(formAviso);
            const submitButton = formAviso.querySelector('.btn-publicar');
            
            // Desabilitar botão durante o envio
            submitButton.disabled = true;
            submitButton.textContent = 'Publicando...';
            
            try {
                const response = await fetch('/admin_personalizado/avisos/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrftoken
                    },
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Limpar formulário
                    formAviso.reset();
                    selectImportancia.className = '';
                    
                    // Recarregar avisos
                    await carregarAvisos();
                    
                    // Mostrar mensagem de sucesso
                    alert('Aviso publicado com sucesso!');
                } else {
                    alert('Erro ao publicar aviso: ' + data.message);
                }
            } catch (error) {
                console.error('Erro:', error);
                alert('Erro ao publicar aviso. Tente novamente.');
            } finally {
                // Reabilitar botão
                submitButton.disabled = false;
                submitButton.textContent = 'Publicar Aviso';
            }
        });
    }

    // --- EVENT LISTENER PARA AÇÕES DOS AVISOS ---
    if (listaAvisosAtivos) {
        listaAvisosAtivos.addEventListener('click', async (e) => {
            const target = e.target.closest('button');
            if (!target) return;
            
            const card = target.closest('.notice-card');
            const id = card.dataset.id;
            
            if (target.classList.contains('delete-btn')) {
                if (!confirm('Tem certeza que deseja mover este aviso para o histórico?')) {
                    return;
                }
                
                try {
                    const response = await fetch(`/admin_personalizado/avisos/${id}/excluir/`, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': csrftoken
                        }
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        await carregarAvisos();
                        alert('Aviso movido para o histórico!');
                    } else {
                        alert('Erro ao excluir aviso: ' + data.message);
                    }
                } catch (error) {
                    console.error('Erro:', error);
                    alert('Erro ao excluir aviso. Tente novamente.');
                }
            }
        });
    }

    // --- EVENT LISTENER PARA MUDANÇA DE IMPORTÂNCIA ---
    if (selectImportancia) {
        selectImportancia.addEventListener('change', (e) => {
            selectImportancia.className = '';
            selectImportancia.classList.add(e.target.value);
        });
    }

    // --- VERIFICAÇÃO DE EXPIRAÇÃO A CADA 30 SEGUNDOS ---
    setInterval(() => {
        carregarAvisos();
    }, 30000);
});
