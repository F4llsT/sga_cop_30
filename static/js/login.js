// Função para armazenar o token JWT
function setAuthToken(access, refresh = null) {
    if (access) {
        localStorage.setItem('access_token', access);
        // Define o token como cookie também, para compatibilidade
        document.cookie = `access_token=${access}; path=/; max-age=86400`; // 24 horas
    }
    if (refresh) {
        localStorage.setItem('refresh_token', refresh);
        document.cookie = `refresh_token=${refresh}; path=/; max-age=604800`; // 7 dias
    }
}

// Função para fazer login
async function loginUser(email, password) {
    try {
        const response = await fetch('/api/token/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: email,
                password: password,
            }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Erro ao fazer login');
        }

        const data = await response.json();
        setAuthToken(data.access, data.refresh);
        
        return data;
    } catch (error) {
        console.error('Erro no login:', error);
        throw error;
    }
}

// Elementos da interface
const container = document.querySelector('.container');
const registrarBtn = document.querySelector('.registrar-btn');
const entrarBtn = document.querySelector('.entrar-btn');
const loginForm = document.getElementById('login-form');
const loginError = document.getElementById('login-error');

// Event listeners para alternar entre login e registro
if (registrarBtn && entrarBtn) {
    registrarBtn.addEventListener('click', () => {
        container.classList.add('ativo');
    });

    entrarBtn.addEventListener('click', () => {
        container.classList.remove('ativo');
    });
}

// Event listener para o formulário de login
if (loginForm) {
    loginForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        
        const email = loginForm.querySelector('input[type="email"]').value;
        const password = loginForm.querySelector('input[type="password"]').value;
        
        try {
            // Mostrar loading
            const submitButton = loginForm.querySelector('button[type="submit"]');
            const originalButtonText = submitButton.innerHTML;
            submitButton.disabled = true;
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Entrando...';
            
            // Fazer login
            await loginUser(email, password);
            
            // Redirecionar para a página inicial após login bem-sucedido
            window.location.href = '/';
            
        } catch (error) {
            console.error('Erro no login:', error);
            if (loginError) {
                loginError.textContent = error.message || 'Erro ao fazer login. Verifique suas credenciais.';
                loginError.style.display = 'block';
            }
            
            // Restaurar botão
            const submitButton = loginForm.querySelector('button[type="submit"]');
            submitButton.disabled = false;
            submitButton.innerHTML = 'Entrar';
        }
    });
}

// Verificar se o usuário já está autenticado ao carregar a página
document.addEventListener('DOMContentLoaded', () => {
    const accessToken = localStorage.getItem('access_token') || getCookie('access_token');
    
    // Se o usuário já estiver autenticado, redireciona para a página inicial
    if (accessToken && window.location.pathname === '/login/') {
        window.location.href = '/';
    }
});

// Função auxiliar para obter cookies
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}