// Função auxiliar para obter cookies
function getCookie(name) {
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
}

// Função auxiliar para validar email
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

document.addEventListener('DOMContentLoaded', () => {
    // --- Lógica para upload de imagem e menu de edição ---
    const imageUploadInput = document.getElementById('image-upload-input');
    const profileImage = document.getElementById('profile-image');
    const defaultAvatar = document.getElementById('default-avatar');
    const fotoPerfilInput = document.querySelector('input[name="foto_perfil"]');
    
    const editPictureBtn = document.getElementById('edit-picture-btn');
    const pictureActionsMenu = document.getElementById('picture-actions-menu');
    const changePictureBtn = document.getElementById('change-picture-btn');
    const removePictureBtn = document.getElementById('remove-picture-btn');

    // Mostrar/esconder menu de ações da foto
    if(editPictureBtn) {
        editPictureBtn.addEventListener('click', (event) => {
            event.stopPropagation();
            pictureActionsMenu.classList.toggle('active');
        });
    }

    // Fechar menu ao clicar fora
    window.addEventListener('click', () => {
        if (pictureActionsMenu && pictureActionsMenu.classList.contains('active')) {
            pictureActionsMenu.classList.remove('active');
        }
    });

    // Abrir seletor de arquivo ao clicar em "Alterar Foto"
    if(changePictureBtn) {
        changePictureBtn.addEventListener('click', () => {
            imageUploadInput.click();
        });
    }

    // Lidar com a seleção de nova imagem
    if(imageUploadInput) {
        imageUploadInput.addEventListener('change', (event) => {
            const file = event.target.files[0];
            if (file) {
                // Verificar o tipo do arquivo
                if (!file.type.match('image.*')) {
                    alert('Por favor, selecione um arquivo de imagem válido.');
                    imageUploadInput.value = ''; // Limpa a seleção
                    return;
                }

                // Verificar o tamanho do arquivo (máximo 5MB)
                if (file.size > 5 * 1024 * 1024) {
                    alert('A imagem deve ter no máximo 5MB.');
                    imageUploadInput.value = ''; // Limpa a seleção
                    return;
                }

                // Copiar o arquivo para o campo do formulário
                if (fotoPerfilInput) {
                    try {
                        // Cria um novo DataTransfer para copiar o arquivo
                        const dataTransfer = new DataTransfer();
                        dataTransfer.items.add(file);
                        fotoPerfilInput.files = dataTransfer.files;
                    } catch (e) {
                        // Fallback para navegadores mais antigos
                        // Cria um novo input file e substitui o antigo
                        const newInput = document.createElement('input');
                        newInput.type = 'file';
                        newInput.name = fotoPerfilInput.name;
                        newInput.id = fotoPerfilInput.id;
                        newInput.accept = 'image/*';
                        newInput.style.display = 'none';
                        
                        // Adiciona o arquivo usando FileList
                        const fileList = new DataTransfer();
                        fileList.items.add(file);
                        newInput.files = fileList.files;
                        
                        // Substitui o input antigo
                        fotoPerfilInput.parentNode.replaceChild(newInput, fotoPerfilInput);
                    }
                }

                // Mostrar preview da imagem
                const reader = new FileReader();
                reader.onload = (e) => {
                    profileImage.src = e.target.result;
                    if(profileImage.style) profileImage.style.display = 'block';
                    if(defaultAvatar.style) defaultAvatar.style.display = 'none';
                };
                reader.readAsDataURL(file);
                
                // Fechar o menu de ações
                if(pictureActionsMenu) {
                    pictureActionsMenu.classList.remove('active');
                }
            }
        });
    }
    
    // Remover foto de perfil
    if(removePictureBtn) {
        removePictureBtn.addEventListener('click', () => {
            if(confirm('Tem certeza que deseja remover sua foto de perfil?')) {
                // Limpa o campo do formulário
                if (fotoPerfilInput) {
                    fotoPerfilInput.value = '';
                    // Limpa também o input customizado
                    if (imageUploadInput) {
                        imageUploadInput.value = '';
                    }
                }
                
                // Atualiza a exibição
                profileImage.src = '';
                if(profileImage.style) profileImage.style.display = 'none';
                if(defaultAvatar.style) defaultAvatar.style.display = 'flex';
                if(pictureActionsMenu) pictureActionsMenu.classList.remove('active');
            }
        });
    }

    // --- Lógica do modal de exclusão de conta ---
    const deleteAccountBtn = document.getElementById('delete-account-btn');
    const modalOverlay = document.getElementById('delete-modal-overlay');
    const cancelDeleteBtn = document.getElementById('cancel-delete-btn');
    const confirmDeleteBtn = document.getElementById('confirm-delete-btn');

    if (deleteAccountBtn) {
        deleteAccountBtn.addEventListener('click', (e) => {
            e.preventDefault();
            modalOverlay.classList.add('active');
        });
    }

    if (cancelDeleteBtn) {
        cancelDeleteBtn.addEventListener('click', () => {
            modalOverlay.classList.remove('active');
        });
    }

    if (confirmDeleteBtn) {
        confirmDeleteBtn.addEventListener('click', () => {
            // Mostra o modal de confirmação
            if (confirm('Tem certeza que deseja excluir permanentemente sua conta? Esta ação não pode ser desfeita.')) {
                // Desabilita o botão para evitar múltiplos cliques
                confirmDeleteBtn.disabled = true;
                confirmDeleteBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Excluindo...';
                
                // Faz a requisição para excluir a conta
                fetch('/usuarios/excluir-conta/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'X-Requested-With': 'XMLHttpRequest',
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({}),
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Erro na requisição');
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.success) {
                        // Redireciona para a página inicial após a exclusão
                        window.location.href = '/';
                    } else {
                        throw new Error(data.error || 'Erro desconhecido');
                    }
                })
                .catch(error => {
                    console.error('Erro:', error);
                    alert('Ocorreu um erro ao tentar excluir sua conta. Por favor, tente novamente.');
                    // Reabilita o botão em caso de erro
                    confirmDeleteBtn.disabled = false;
                    confirmDeleteBtn.innerHTML = '<i class="fa-solid fa-trash"></i> Excluir';
                });
            }
        });
    }

    if(modalOverlay) {
        modalOverlay.addEventListener('click', (event) => {
            if (event.target === modalOverlay) {
                modalOverlay.classList.remove('active');
            }
        });
    }

// --- Lógica de busca automática de CEP ---
const cepInput = document.getElementById('id_cep');

if (cepInput) {
    // Formatar CEP e buscar automaticamente
    cepInput.addEventListener('input', function(e) {
        // Formatar CEP
        let value = e.target.value.replace(/\D/g, '');
        if (value.length > 5) {
            value = value.substring(0, 5) + '-' + value.substring(5, 8);
        }
        e.target.value = value;

        // Buscar CEP automaticamente quando tiver 9 caracteres (00000-000)
        if (e.target.value.length === 9) {
            const cep = e.target.value.replace(/\D/g, '');
            buscarCep(cep);
        }
    });
    
    // Função para buscar CEP
    function buscarCep(cep) {
        if (cep.length !== 8) {
            return;
        }
        
        // Mostrar loading
        cepInput.disabled = true;
        
        // Fazer requisição para a API ViaCEP
        fetch(`https://viacep.com.br/ws/${cep}/json/`)
            .then(response => response.json())
            .then(data => {
                if (data.erro) {
                    throw new Error('CEP não encontrado');
                }
                
                // Preencher os campos com os dados do CEP
                document.getElementById('id_logradouro').value = data.logradouro || '';
                document.getElementById('id_bairro').value = data.bairro || '';
                document.getElementById('id_cidade').value = data.localidade || '';
                document.getElementById('id_estado').value = data.uf || '';
                
                // Focar no campo de número
                document.getElementById('id_numero').focus();
            })
            .catch(error => {
                console.error('Erro ao buscar CEP:', error);
                // Não mostrar alerta, apenas limpar os campos
                document.getElementById('id_logradouro').value = '';
                document.getElementById('id_bairro').value = '';
                document.getElementById('id_cidade').value = '';
                document.getElementById('id_estado').value = '';
            })
            .finally(() => {
                cepInput.disabled = false;
            });
    }
}
    // --- Validação de formulário ---
    const form = document.getElementById('profile-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            let isValid = true;
            
            // Garantir que a data está no formato correto antes do submit
            const dataNascimentoField = document.getElementById('id_data_nascimento');
            if (dataNascimentoField && dataNascimentoField.value) {
                // Remove qualquer validação HTML5 que possa estar bloqueando
                dataNascimentoField.setCustomValidity('');
                
                // Valida a data
                if (!validateBirthDate(dataNascimentoField)) {
                    dataNascimentoField.classList.add('is-invalid');
                    isValid = false;
                } else {
                    // Garante que está no formato DD/MM/YYYY
                    const value = dataNascimentoField.value.trim();
                    if (value && value.length === 10 && value.includes('/')) {
                        // Já está formatado, apenas remove classes de erro
                        dataNascimentoField.classList.remove('is-invalid');
                    }
                }
            }
            
            // Validação básica de campos obrigatórios
            const requiredFields = form.querySelectorAll('[required]');
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    field.classList.add('is-invalid');
                    isValid = false;
                } else {
                    field.classList.remove('is-invalid');
                }
            });
            
            // Validação de email
            const emailField = document.getElementById('id_email');
            if (emailField && !isValidEmail(emailField.value)) {
                emailField.classList.add('is-invalid');
                isValid = false;
            }
            
            if (!isValid) {
                e.preventDefault();
                // Foca no primeiro campo com erro
                const firstInvalid = form.querySelector('.is-invalid');
                if (firstInvalid) {
                    firstInvalid.focus();
                    firstInvalid.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
                return false;
            } else {
                // Remove qualquer validação HTML5 antes de enviar
                if (dataNascimentoField) {
                    dataNascimentoField.setCustomValidity('');
                }
                
                // Mostrar loading no botão de salvar
                const saveBtn = document.getElementById('save-all-btn');
                if (saveBtn) {
                    saveBtn.disabled = true;
                    saveBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Salvando...';
                }
                
                // Permite o submit
                return true;
            }
        });
    }
});

// ===== FUNÇÕES DE MÁSCARA DINÂMICA =====

/**
 * Aplica máscara de telefone que aceita apenas números e formata automaticamente
 * Formato: (00) 00000-0000 para celular ou (00) 0000-0000 para fixo
 */
function applyPhoneMask(input) {
    // Remove qualquer formatação existente e mantém apenas números
    function formatPhone(value) {
        const numbers = value.replace(/\D/g, '');
        
        if (numbers.length === 0) return '';
        if (numbers.length <= 2) return `(${numbers}`;
        if (numbers.length <= 6) return `(${numbers.slice(0, 2)}) ${numbers.slice(2)}`;
        if (numbers.length <= 10) {
            // Telefone fixo: (00) 0000-0000
            return `(${numbers.slice(0, 2)}) ${numbers.slice(2, 6)}-${numbers.slice(6)}`;
        } else {
            // Celular: (00) 00000-0000
            return `(${numbers.slice(0, 2)}) ${numbers.slice(2, 7)}-${numbers.slice(7, 11)}`;
        }
    }
    
    // Evento de input - formata enquanto digita
    input.addEventListener('input', function(e) {
        const cursorPosition = e.target.selectionStart;
        const oldValue = e.target.value;
        const oldLength = oldValue.length;
        
        // Formata o valor
        const formatted = formatPhone(e.target.value);
        e.target.value = formatted;
        
        // Ajusta a posição do cursor
        const newLength = formatted.length;
        const lengthDiff = newLength - oldLength;
        const newPosition = Math.max(0, cursorPosition + lengthDiff);
        e.target.setSelectionRange(newPosition, newPosition);
    });
    
    // Evento de keydown - bloqueia caracteres não numéricos (exceto teclas especiais)
    input.addEventListener('keydown', function(e) {
        // Permite teclas especiais (backspace, delete, tab, setas, etc)
        const allowedKeys = [
            'Backspace', 'Delete', 'Tab', 'Escape', 'Enter',
            'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown',
            'Home', 'End'
        ];
        
        if (allowedKeys.includes(e.key)) {
            return;
        }
        
        // Permite Ctrl/Cmd + A, C, V, X
        if ((e.ctrlKey || e.metaKey) && ['a', 'c', 'v', 'x'].includes(e.key.toLowerCase())) {
            return;
        }
        
        // Bloqueia qualquer coisa que não seja número
        if (!/[0-9]/.test(e.key)) {
            e.preventDefault();
        }
    });
    
    // Evento de paste - formata quando cola texto
    input.addEventListener('paste', function(e) {
        e.preventDefault();
        const pastedText = (e.clipboardData || window.clipboardData).getData('text');
        const numbers = pastedText.replace(/\D/g, '');
        if (numbers) {
            input.value = formatPhone(numbers);
            // Dispara evento input para garantir formatação
            input.dispatchEvent(new Event('input'));
        }
    });
}

/**
 * Aplica máscara de data de nascimento que aceita apenas números e formata automaticamente
 * Formato: DD/MM/AAAA
 */
function applyDateMask(input) {
    // Remove qualquer formatação existente e mantém apenas números
    function formatDate(value) {
        const numbers = value.replace(/\D/g, '');
        
        if (numbers.length === 0) return '';
        if (numbers.length <= 2) return numbers;
        if (numbers.length <= 4) return `${numbers.slice(0, 2)}/${numbers.slice(2)}`;
        return `${numbers.slice(0, 2)}/${numbers.slice(2, 4)}/${numbers.slice(4, 8)}`;
    }
    
    // Valida se a data é válida
    function isValidDate(day, month, year) {
        if (!day || !month || !year) return false;
        
        const d = parseInt(day, 10);
        const m = parseInt(month, 10);
        const y = parseInt(year, 10);
        
        // Validação básica
        if (d < 1 || d > 31) return false;
        if (m < 1 || m > 12) return false;
        if (y < 1900 || y > new Date().getFullYear()) return false;
        
        // Validação de dias por mês
        const daysInMonth = new Date(y, m, 0).getDate();
        if (d > daysInMonth) return false;
        
        // Verifica se a data não é futura
        const date = new Date(y, m - 1, d);
        const today = new Date();
        today.setHours(23, 59, 59, 999);
        
        if (date > today) return false;
        
        // Verifica se a data é válida (ex: 31/02 não existe)
        return date.getDate() === d && 
               date.getMonth() === m - 1 && 
               date.getFullYear() === y;
    }
    
    // Evento de input - formata enquanto digita
    input.addEventListener('input', function(e) {
        const cursorPosition = e.target.selectionStart;
        const oldValue = e.target.value;
        const oldLength = oldValue.length;
        
        // Limita a 8 dígitos
        let numbers = e.target.value.replace(/\D/g, '');
        if (numbers.length > 8) {
            numbers = numbers.slice(0, 8);
        }
        
        // Formata o valor
        const formatted = formatDate(numbers);
        e.target.value = formatted;
        
        // Validação visual
        if (formatted.length === 10) {
            const [day, month, year] = formatted.split('/');
            if (isValidDate(day, month, year)) {
                e.target.classList.remove('is-invalid');
                e.target.setCustomValidity('');
            } else {
                e.target.classList.add('is-invalid');
                e.target.setCustomValidity('Data inválida');
            }
        } else {
            e.target.classList.remove('is-invalid');
            e.target.setCustomValidity('');
        }
        
        // Ajusta a posição do cursor
        const newLength = formatted.length;
        const lengthDiff = newLength - oldLength;
        const newPosition = Math.max(0, cursorPosition + lengthDiff);
        e.target.setSelectionRange(newPosition, newPosition);
    });
    
    // Evento de keydown - bloqueia caracteres não numéricos (exceto teclas especiais)
    input.addEventListener('keydown', function(e) {
        // Permite teclas especiais
        const allowedKeys = [
            'Backspace', 'Delete', 'Tab', 'Escape', 'Enter',
            'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown',
            'Home', 'End'
        ];
        
        if (allowedKeys.includes(e.key)) {
            return;
        }
        
        // Permite Ctrl/Cmd + A, C, V, X
        if ((e.ctrlKey || e.metaKey) && ['a', 'c', 'v', 'x'].includes(e.key.toLowerCase())) {
            return;
        }
        
        // Bloqueia qualquer coisa que não seja número
        if (!/[0-9]/.test(e.key)) {
            e.preventDefault();
        }
    });
    
    // Evento de paste - formata quando cola texto
    input.addEventListener('paste', function(e) {
        e.preventDefault();
        const pastedText = (e.clipboardData || window.clipboardData).getData('text');
        const numbers = pastedText.replace(/\D/g, '').slice(0, 8);
        if (numbers) {
            input.value = formatDate(numbers);
            input.dispatchEvent(new Event('input'));
        }
    });
    
    // Validação ao sair do campo
    input.addEventListener('blur', function() {
        const value = this.value;
        if (value && value.length === 10) {
            const [day, month, year] = value.split('/');
            if (!isValidDate(day, month, year)) {
                this.classList.add('is-invalid');
                this.setCustomValidity('Por favor, insira uma data válida');
            } else {
                // Validação de idade mínima
                const date = new Date(parseInt(year, 10), parseInt(month, 10) - 1, parseInt(day, 10));
                const today = new Date();
                const age = today.getFullYear() - date.getFullYear();
                const monthDiff = today.getMonth() - date.getMonth();
                const dayDiff = today.getDate() - date.getDate();
                const actualAge = age - (monthDiff < 0 || (monthDiff === 0 && dayDiff < 0) ? 1 : 0);
                
                if (actualAge < 12) {
                    this.classList.add('is-invalid');
                    this.setCustomValidity('Você deve ter pelo menos 12 anos');
                } else {
                    this.classList.remove('is-invalid');
                    this.setCustomValidity('');
                }
            }
        } else if (value && value.length > 0) {
            this.classList.add('is-invalid');
            this.setCustomValidity('Data incompleta');
        } else {
            this.classList.remove('is-invalid');
            this.setCustomValidity('');
        }
    });
}

// Validação de data de nascimento (função auxiliar para validação no submit)
function validateBirthDate(input) {
    const value = input.value;
    if (!value || value.length !== 10) {
        return false;
    }
    
    const [day, month, year] = value.split('/').map(Number);
    const date = new Date(year, month - 1, day);
    const today = new Date();
    const minDate = new Date();
    minDate.setFullYear(today.getFullYear() - 120);
    
    // Verifica se a data é válida
    const isValid = date <= today && 
                   date >= minDate && 
                   date.getDate() === day && 
                   date.getMonth() === month - 1 && 
                   date.getFullYear() === year;
    
    if (!isValid) {
        input.setCustomValidity('Por favor, insira uma data de nascimento válida');
        return false;
    }
    
    // Valida idade mínima
    const age = today.getFullYear() - year;
    const monthDiff = today.getMonth() - (month - 1);
    const dayDiff = today.getDate() - day;
    const actualAge = age - (monthDiff < 0 || (monthDiff === 0 && dayDiff < 0) ? 1 : 0);
    
    if (actualAge < 12) {
        input.setCustomValidity('Você deve ter pelo menos 12 anos');
        return false;
    }
    
    input.setCustomValidity('');
    return true;
}

// Inicialização das máscaras quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    const phoneInput = document.getElementById('id_telefone');
    const birthDateInput = document.getElementById('id_data_nascimento');
    
    // Aplica máscara de telefone
    if (phoneInput) {
        applyPhoneMask(phoneInput);
    }
    
    // Aplica máscara de data de nascimento
    if (birthDateInput) {
        applyDateMask(birthDateInput);
        
        // Validação adicional no submit do formulário
        const form = document.getElementById('profile-form');
        if (form) {
            form.addEventListener('submit', function(e) {
                if (birthDateInput && birthDateInput.value && !validateBirthDate(birthDateInput)) {
                    e.preventDefault();
                    birthDateInput.focus();
                    return false;
                }
            });
        }
    }
});