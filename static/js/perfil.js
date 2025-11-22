document.addEventListener('DOMContentLoaded', () => {
    // --- Lógica para upload de imagem e menu de edição ---
    const imageUploadInput = document.getElementById('image-upload-input');
    const profileImage = document.getElementById('profile-image');
    const defaultAvatar = document.getElementById('default-avatar');
    
    const editPictureBtn = document.getElementById('edit-picture-btn');
    const pictureActionsMenu = document.getElementById('picture-actions-menu');
    const changePictureBtn = document.getElementById('change-picture-btn');
    const removePictureBtn = document.getElementById('remove-picture-btn');

    if(editPictureBtn) {
        editPictureBtn.addEventListener('click', (event) => {
            event.stopPropagation();
            pictureActionsMenu.classList.toggle('active');
        });
    }

    window.addEventListener('click', () => {
        if (pictureActionsMenu && pictureActionsMenu.classList.contains('active')) {
            pictureActionsMenu.classList.remove('active');
        }
    });

    if(changePictureBtn) {
        changePictureBtn.addEventListener('click', () => {
            imageUploadInput.click();
        });
    }

    if(imageUploadInput) {
        imageUploadInput.addEventListener('change', (event) => {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    profileImage.src = e.target.result;
                    if(profileImage.style) profileImage.style.display = 'block';
                    if(defaultAvatar.style) defaultAvatar.style.display = 'none';
                };
                reader.readAsDataURL(file);
            }
        });
    }
    
    if(removePictureBtn) {
        removePictureBtn.addEventListener('click', () => {
            if(confirm('Tem certeza que deseja remover sua foto de perfil?')) {
                profileImage.src = '';
                if(profileImage.style) profileImage.style.display = 'none';
                if(defaultAvatar.style) defaultAvatar.style.display = 'flex';
                if(pictureActionsMenu) pictureActionsMenu.classList.remove('active');
                alert('Foto de perfil removida.');
            }
        });
    }

    // --- Lógica do modal de exclusão de conta ---
    const deleteAccountBtn = document.getElementById('delete-account-btn');
    const modalOverlay = document.getElementById('delete-modal-overlay');
    const cancelDeleteBtn = document.getElementById('cancel-delete-btn');
    const confirmDeleteBtn = document.getElementById('confirm-delete-btn');

    if (deleteAccountBtn) {
        deleteAccountBtn.addEventListener('click', () => {
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
            alert('Conta excluída com sucesso. (Simulação)');
            modalOverlay.classList.remove('active');
        });
    }

    if(modalOverlay) {
        modalOverlay.addEventListener('click', (event) => {
            if (event.target === modalOverlay) {
                modalOverlay.classList.remove('active');
            }
        });
    }
    
    // --- Lógica do botão de salvar ---
    const saveBtn = document.getElementById('save-all-btn');
    if (saveBtn) {
        saveBtn.addEventListener('click', () => {
            alert('Alterações salvas com sucesso! (Simulação)');
        });
    }
});