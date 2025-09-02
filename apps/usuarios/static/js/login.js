const container = document.querySelector('.container');
const registrarBtn = document.querySelector('.registrar-btn');
const entrarBtn = document.querySelector('.entrar-btn');

registrarBtn.addEventListener('click', ()=> {
    container.classList.add('ativo');
});

entrarBtn.addEventListener('click', ()=> {
    container.classList.remove('ativo');
});