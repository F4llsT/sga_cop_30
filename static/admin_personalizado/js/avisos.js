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
            console.log('Carregando avisos de: /meu-admin/api/avisos/');
            const response = await fetch('/meu-admin/api/avisos/');
            
            if (!response.ok) {
                throw new Error(`Erro HTTP: ${response.status}`);
            }
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
                // Convert FormData to plain object
                const formDataObj = {};
                formData.forEach((value, key) => {
                    formDataObj[key] = value;
                });

                // Send as JSON - Using the correct URL pattern
                const response = await fetch('/meu-admin/api/avisos/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrftoken,
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: JSON.stringify(formDataObj)
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Limpar formulário
                    formAviso.reset();
                    selectImportancia.className = '';
                    
                    // Carregar avisos iniciais
                    await carregarAvisos();
                    
                    // Reset form and UI state
                    document.getElementById('aviso-titulo').value = '';
                    document.getElementById('aviso-mensagem').value = '';
                    document.getElementById('aviso-importancia').value = 'info';
                    document.getElementById('aviso-expiracao').value = '';
                    document.getElementById('aviso-horario').value = '';
                    document.getElementById('aviso-fixo').checked = false;
                    
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
            
            if (target.classList.contains('pin-btn')) {
                try {
                    const response = await fetch(`/meu-admin/avisos/${id}/fixar/`, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': csrftoken,
                            'Content-Type': 'application/json',
                            'X-Requested-With': 'XMLHttpRequest'
                        },
                        body: JSON.stringify({})
                    });

                    if (!response.ok) {
                        throw new Error(`Erro HTTP! status: ${response.status}`);
                    }

                    const data = await response.json();
                    
                    if (data.success) {
                        // Atualiza o estado visual do botão
                        target.classList.toggle('pinned');
                        // Recarrega a lista para garantir que os itens fixos fiquem no topo
                        await carregarAvisos();
                    } else {
                        throw new Error(data.message || 'Erro ao atualizar o estado de fixo');
                    }
                } catch (error) {
                    console.error('Erro ao fixar/desafixar aviso:', error);
                    // Mostra mensagem de erro
                    const errorDiv = document.createElement('div');
                    errorDiv.className = 'alert alert-danger';
                    errorDiv.textContent = `Erro ao atualizar o aviso: ${error.message}`;
                    document.querySelector('.avisos-container').prepend(errorDiv);
                    // Remove a mensagem de erro após 5 segundos
                    setTimeout(() => errorDiv.remove(), 5000);
                }
            } else if (target.classList.contains('delete-btn')) {
                if (!confirm('Tem certeza que deseja mover este aviso para o histórico?')) {
                    return;
                }
                
                try {
                    if (!confirm('Tem certeza que deseja mover este aviso para o histórico?')) {
                        return;
                    }

                    const response = await fetch(`/meu-admin/avisos/${id}/excluir/`, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': csrftoken,
                            'Content-Type': 'application/json',
                            'X-Requested-With': 'XMLHttpRequest'
                        },
                        body: JSON.stringify({})
                    });

                    if (!response.ok) {
                        throw new Error(`Erro HTTP! status: ${response.status}`);
                    }

                    const data = await response.json();
                    
                    if (data.success) {
                        await carregarAvisos();
                        // Show success message using a more elegant notification if available
                        const successDiv = document.createElement('div');
                        successDiv.className = 'alert alert-success';
                        successDiv.textContent = 'Aviso movido para o histórico com sucesso!';
                        document.querySelector('.avisos-container').prepend(successDiv);
                        // Remove the message after 3 seconds
                        setTimeout(() => successDiv.remove(), 3000);
                    } else {
                        throw new Error(data.message || 'Erro desconhecido ao excluir aviso');
                    }
                } catch (error) {
                    console.error('Erro ao excluir aviso:', error);
                    // Show error message in the UI
                    const errorDiv = document.createElement('div');
                    errorDiv.className = 'alert alert-danger';
                    errorDiv.textContent = `Erro ao excluir aviso: ${error.message}`;
                    document.querySelector('.avisos-container').prepend(errorDiv);
                    // Remove the error message after 5 seconds
                    setTimeout(() => errorDiv.remove(), 5000);
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
