const container = document.querySelector('.container');
const registrarBtn = document.querySelector('.registrar-btn');
const entrarBtn = document.querySelector('.entrar-btn');

registrarBtn.addEventListener('click', ()=> {
    container.classList.add('ativo');
});

entrarBtn.addEventListener('click', ()=> {
    container.classList.remove('ativo');
});

// Adiciona o código para a tela de login
const loginForm = document.getElementById('login-form');

// Escuta o evento de submissão do formulário
loginForm.addEventListener('submit', (event) => {
    // Impede o envio padrão do formulário, que recarregaria a página
    event.preventDefault(); 

    // Adiciona um pequeno atraso para simular o processamento do login (opcional)
    setTimeout(() => {
        // Redireciona o usuário para a página principal
        window.location.href = 'home.html';
    }, 500); // 500 milissegundos de atraso
});