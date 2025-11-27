// ===== SCRIPTS GERAIS DO PAINEL ADMIN =====

document.addEventListener('DOMContentLoaded', function() {
    
    // ===== MENU LATERAL MOBILE =====
    const menuButton = document.getElementById('admin-menu-button');
    const sidebar = document.querySelector('.sidebar');
    const adminWrapper = document.querySelector('.admin-wrapper');
    
    if (menuButton && sidebar) {
        menuButton.addEventListener('click', function() {
            sidebar.classList.toggle('active');
            adminWrapper.classList.toggle('sidebar-active');
        });
        
        // Fechar menu ao clicar fora
        document.addEventListener('click', function(e) {
            if (!sidebar.contains(e.target) && !menuButton.contains(e.target)) {
                sidebar.classList.remove('active');
                adminWrapper.classList.remove('sidebar-active');
            }
        });
    }
    
    // ===== HIGHLIGHT DO MENU ATIVO =====
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.sidebar-nav .nav-link');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
    
    // ===== INICIALIZAÇÃO DATATABLES =====
    if (typeof $.fn.DataTable !== 'undefined') {
        // Inicializa todas as tabelas com a classe 'datatable'
        $('.datatable').each(function() {
            const table = $(this);
            
            // Configuração padrão
            const config = {
                language: typeof dataTablePtBr !== 'undefined' ? dataTablePtBr : {
                    "sEmptyTable": "Nenhum registro encontrado",
                    "sInfo": "Mostrando de _START_ até _END_ de _TOTAL_ registros",
                    "sInfoEmpty": "Mostrando 0 até 0 de 0 registros",
                    "sInfoFiltered": "(Filtrados de _MAX_ registros)",
                    "sLengthMenu": "_MENU_ resultados por página",
                    "sLoadingRecords": "Carregando...",
                    "sProcessing": "Processando...",
                    "sZeroRecords": "Nenhum registro encontrado",
                    "sSearch": "Pesquisar",
                    "oPaginate": {
                        "sNext": "Próximo",
                        "sPrevious": "Anterior",
                        "sFirst": "Primeiro",
                        "sLast": "Último"
                    }
                },
                responsive: true,
                pageLength: 10,
                lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "Todos"]],
                order: [[0, 'desc']],
                dom: '<"row"<"col-sm-12 col-md-6"l><"col-sm-12 col-md-6"f>>' +
                     '<"row"<"col-sm-12"tr>>' +
                     '<"row"<"col-sm-12 col-md-5"i><"col-sm-12 col-md-7"p>>'
            };
            
            // Inicializa a tabela
            table.DataTable(config);
        });
    }
    
    // ===== CONFIRMAÇÃO DE EXCLUSÃO =====
    const deleteButtons = document.querySelectorAll('[data-confirm-delete]');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm-delete') || 'Tem certeza que deseja excluir este item?';
            
            if (!confirm(message)) {
                e.preventDefault();
                return false;
            }
        });
    });
    
    // ===== TOOLTIPS =====
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // ===== NOTIFICAÇÕES FLASH =====
    const flashMessages = document.querySelectorAll('.flash-message');
    
    flashMessages.forEach(message => {
        // Auto-remove após 5 segundos
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => {
                message.remove();
            }, 300);
        }, 5000);
        
        // Fechar manualmente
        const closeBtn = message.querySelector('.flash-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                message.style.opacity = '0';
                setTimeout(() => {
                    message.remove();
                }, 300);
            });
        }
    });
    
    // ===== FORMULÁRIOS COM AJAX =====
    const ajaxForms = document.querySelectorAll('[data-ajax-form]');
    
    ajaxForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const submitBtn = form.querySelector('[type="submit"]');
            const originalText = submitBtn.innerHTML;
            
            // Loading state
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processando...';
            
            // Envia formulário via AJAX
            fetch(form.action, {
                method: form.method,
                body: new FormData(form),
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Sucesso
                    showNotification(data.message || 'Operação realizada com sucesso!', 'success');
                    
                    // Recarrega ou redireciona se necessário
                    if (data.reload) {
                        setTimeout(() => window.location.reload(), 1500);
                    } else if (data.redirect) {
                        setTimeout(() => window.location.href = data.redirect, 1500);
                    }
                } else {
                    // Erro
                    showNotification(data.message || 'Ocorreu um erro!', 'error');
                }
            })
            .catch(error => {
                console.error('Erro:', error);
                showNotification('Erro de conexão. Tente novamente!', 'error');
            })
            .finally(() => {
                // Restaura botão
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            });
        });
    });
    
    // ===== FUNÇÃO DE NOTIFICAÇÃO =====
    function showNotification(message, type = 'info') {
        // Remove notificações existentes
        const existingNotifications = document.querySelectorAll('.notification-toast');
        existingNotifications.forEach(n => n.remove());
        
        // Cria nova notificação
        const notification = document.createElement('div');
        notification.className = `notification-toast notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fa-solid ${getIconForType(type)}"></i>
                <span>${message}</span>
            </div>
            <button class="notification-close">&times;</button>
        `;
        
        // Adiciona ao DOM
        document.body.appendChild(notification);
        
        // Evento de fechar
        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.addEventListener('click', () => {
            notification.remove();
        });
        
        // Auto-remove
        setTimeout(() => {
            if (document.body.contains(notification)) {
                notification.remove();
            }
        }, 5000);
    }
    
    function getIconForType(type) {
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-exclamation-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };
        return icons[type] || icons.info;
    }
    
    // ===== EXPORTAR FUNÇÕES GLOBAIS =====
    window.showNotification = showNotification;
    
    // ===== MÁSCARA DE CAMPOS =====
    const phoneInputs = document.querySelectorAll('[data-mask="phone"]');
    phoneInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 0) {
                value = value.match(/(\d{0,2})(\d{0,5})(\d{0,4})/);
                value = !value[2] ? value[1] : '(' + value[1] + ') ' + value[2] + (value[3] ? '-' + value[3] : '');
            }
            e.target.value = value;
        });
    });
    
    const cpfInputs = document.querySelectorAll('[data-mask="cpf"]');
    cpfInputs.forEach(input => {
        input.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 0) {
                value = value.match(/(\d{0,3})(\d{0,3})(\d{0,3})(\d{0,2})/);
                value = !value[2] ? value[1] : value[1] + '.' + value[2] + (value[3] ? '.' + value[3] : '') + (value[4] ? '-' + value[4] : '');
            }
            e.target.value = value;
        });
    });
    
    // ===== COLLAPSE SIDEBAR =====
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebarCollapsedClass = 'sidebar-collapsed';
    
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            document.body.classList.toggle(sidebarCollapsedClass);
            
            // Salva preferência no localStorage
            const isCollapsed = document.body.classList.contains(sidebarCollapsedClass);
            localStorage.setItem('sidebar-collapsed', isCollapsed);
        });
        
        // Restora preferência salva
        const isCollapsed = localStorage.getItem('sidebar-collapsed') === 'true';
        if (isCollapsed) {
            document.body.classList.add(sidebarCollapsedClass);
        }
    }
    
    console.log('Admin scripts loaded successfully!');
});

// ===== FUNÇÕES GLOBAIS =====

// Formatação de data
function formatDate(date) {
    if (!date) return '';
    const d = new Date(date);
    return d.toLocaleDateString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Formatação de moeda
function formatMoney(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

// Copiar para clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copiado para a área de transferência!', 'success');
    }).catch(() => {
        showNotification('Erro ao copiar!', 'error');
    });
}

// Exportar funções globais
window.formatDate = formatDate;
window.formatMoney = formatMoney;
window.copyToClipboard = copyToClipboard;
