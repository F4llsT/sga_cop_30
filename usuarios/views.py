# usuarios/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

def login_view(request):
    if request.method == 'POST':
        usuario_nome = request.POST.get('username')
        senha_user = request.POST.get('password')

        user = authenticate(request, username=usuario_nome, password=senha_user)

        if user is not None:
            login(request, user)
            # Redireciona para a página inicial após o login
            return redirect('pagina_inicial')
        else:
            messages.error(request, 'Usuário ou senha inválidos.')
            return render(request, 'usuarios/login.html')

    return render(request, 'usuarios/login.html')

def cadastro_view(request):
    if request.method == 'POST':
        usuario_nome = request.POST.get('username')
        email_user = request.POST.get('email')
        senha1 = request.POST.get('password')
        senha2 = request.POST.get('password-confirm')

        if senha1 != senha2:
            messages.error(request, 'As senhas não coincidem!')
            return redirect('cadastro')

        if User.objects.filter(username=usuario_nome).exists():
            messages.error(request, 'Este nome de usuário já está em uso.')
            return redirect('cadastro')

        user = User.objects.create_user(username=usuario_nome, email=email_user, password=senha1)
        # A linha user.save() é desnecessária aqui, create_user já salva.
        
        messages.success(request, 'Cadastro realizado com sucesso! Faça o login.')
        return redirect('login')

    return render(request, 'usuarios/cadastro.html')

def logout_view(request):
    logout(request)
    messages.info(request, 'Você saiu da sua conta.')
    return redirect('login')

# Em core/views.py
from django.shortcuts import render

def pagina_inicial(request):
    # Esta view irá renderizar um arquivo HTML chamado pagina_inicial.html
    return render(request, 'pagina_inicial.html')