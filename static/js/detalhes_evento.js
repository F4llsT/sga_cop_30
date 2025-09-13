document.addEventListener('DOMContentLoaded', function() {
    const favoriteButton = document.getElementById('favorite-button');
    let isFavorited = false; // Estado inicial (não favoritado)

    // Função para atualizar a aparência do botão
    function updateButtonState() {
        if (isFavorited) {
            favoriteButton.classList.add('favorited');
            favoriteButton.querySelector('.text').textContent = 'Agendado';
        } else {
            favoriteButton.classList.remove('favorited');
            favoriteButton.querySelector('.text').textContent = 'Favoritar';
        }
    }

    // Adiciona o evento de clique ao botão
    favoriteButton.addEventListener('click', function() {
        // Inverte o estado atual
        isFavorited = !isFavorited;
        
        // Atualiza a aparência do botão
        updateButtonState();

        // Futuramente, aqui você fará a chamada ao backend para salvar o estado
        console.log('Evento favoritado:', isFavorited);
    });

    // Garante que o estado inicial do botão esteja correto
    updateButtonState();
});