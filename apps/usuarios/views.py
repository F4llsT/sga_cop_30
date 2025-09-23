from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as BaseLoginView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse

from .models import Usuario, Perfil
from .forms import UserRegistrationForm, UserLoginForm, UserUpdateForm, ProfileUpdateForm

def home(request):
    """
    Exibe a página inicial.
    """
    return render(request, 'home.html')

class LoginView(BaseLoginView):
    """
    Exibe o formulário de login e processa a tentativa de login.
    """
    form_class = UserLoginForm
    template_name = 'login.html'
    redirect_authenticated_user = True
    
    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        if self.redirect_authenticated_user and self.request.user.is_authenticated:
            return redirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)
    
    def get_success_url(self):
        next_url = self.request.POST.get('next') or self.request.GET.get('next')
        return next_url or reverse_lazy('home')
    
    def form_valid(self, form):
        """
        O usuário foi autenticado com sucesso.
        """
        from rest_framework_simplejwt.tokens import RefreshToken
        from django.http import JsonResponse
        
        # Obtém o usuário autenticado
        user = form.get_user()
        
        # Faz o login do usuário na sessão
        login(self.request, user)
        
        # Gera os tokens JWT
        refresh = RefreshToken.for_user(user)
        
        # Mensagem de boas-vindas personalizada
        messages.success(self.request, f'Bem-vindo(a) de volta, {user.nome}!')
        
        # Verifica se é uma requisição AJAX (para API)
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'nome': user.nome
                }
            })
        
        # Para requisições normais, armazena o token no localStorage via JavaScript
        response = super().form_valid(form)
        response.set_cookie('access_token', str(refresh.access_token), httponly=True, max_age=86400)  # 24 horas
        response.set_cookie('refresh_token', str(refresh), httponly=True, max_age=604800)  # 7 dias
        
        return response
    
    def form_invalid(self, form):
        """
        O formulário é inválido.
        """
        messages.error(self.request, 'Email ou senha inválidos. Por favor, tente novamente.')
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['login_form'] = self.get_form()
        context['register_form'] = UserRegistrationForm()
        return context

class RegisterView(FormView):
    """
    Exibe o formulário de registro e processa o cadastro de novos usuários.
    """
    form_class = UserRegistrationForm
    template_name = 'login.html'
    success_url = reverse_lazy('home')
    
    @method_decorator(csrf_protect)
    def dispatch(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect(self.get_success_url())
        return super().dispatch(*args, **kwargs)
    
    def form_valid(self, form):
        """
        O formulário é válido, cria o usuário e faz login.
        """
        # Salva o usuário
        user = form.save()
        
        # Faz o login do usuário
        login(self.request, user)
        
        # Se for uma requisição AJAX, retorna JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'redirect_url': str(self.get_success_url())
            })
            
        # Mensagem de sucesso para requisições normais
        messages.success(
            self.request, 
            f'Conta criada com sucesso! Bem-vindo(a), {user.nome}!',
            extra_tags='register-success'
        )
        
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """
        O formulário é inválido.
        """
        # Se for uma requisição AJAX, retorna erros em JSON
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
            
        # Para requisições normais, mantém o comportamento original
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(
                    self.request, 
                    f'{form.fields[field].label if field in form.fields else field}: {error}',
                    extra_tags='register-error'
                )
        
        return self.render_to_response(self.get_context_data(register_form=form))
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Garante que o formulário de login esteja disponível no template
        if 'login_form' not in context:
            context['login_form'] = UserLoginForm()
        return context

def logout_view(request):
    """
    Faz logout do usuário e redireciona para a página inicial.
    """
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'Você saiu da sua conta com sucesso.')
    return redirect('home')

class ProfileView(LoginRequiredMixin, UpdateView):
    """
    Exibe e atualiza o perfil do usuário.
    """
    model = Usuario
    form_class = UserUpdateForm
    template_name = 'profile.html'
    success_url = reverse_lazy('usuarios:profile')
    
    def get_object(self, queryset=None):
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Adiciona o formulário de perfil ao contexto
        if 'profile_form' not in context:
            context['profile_form'] = self.get_profile_form()
            
        return context
    
    def get_profile_form(self):
        """
        Retorna uma instância do formulário de perfil.
        """
        # Obtém ou cria o perfil do usuário
        perfil, created = Perfil.objects.get_or_create(usuario=self.request.user)
        
        # Retorna o formulário de perfil
        if self.request.method == 'POST':
            return ProfileUpdateForm(
                self.request.POST,
                self.request.FILES,
                instance=perfil
            )
        else:
            return ProfileUpdateForm(instance=perfil)
    
    def post(self, request, *args, **kwargs):
        """Processa o formulário de atualização do perfil."""
        self.object = self.get_object()
        
        # Obtém os formulários
        form = self.get_form()
        profile_form = self.get_profile_form()
        
        # Valida os formulários
        if form.is_valid() and profile_form.is_valid():
            return self.form_valid(form, profile_form)
        return self.form_invalid(form, profile_form)
    
    def form_valid(self, form, profile_form):
        """Salva os dados quando ambos os formulários são válidos."""
        # Salva o usuário
        self.object = form.save()
        
        # Salva o perfil
        profile_form.save()
        
        # Mensagem de sucesso
        messages.success(
            self.request, 
            'Seu perfil foi atualizado com sucesso!'
        )
        
        return redirect(self.get_success_url())
    
    def form_invalid(self, form, profile_form):
        """Lida com formulários inválidos, exibindo mensagens de erro."""
        # Adiciona as mensagens de erro
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(
                    self.request, 
                    f'{form.fields[field].label if field in form.fields else field}: {error}'
                )
                
        for field, errors in profile_form.errors.items():
            for error in errors:
                messages.error(
                    self.request, 
                    f'{profile_form.fields[field].label if field in profile_form.fields else field}: {error}'
                )
        
        return self.render_to_response(self.get_context_data(form=form, profile_form=profile_form))