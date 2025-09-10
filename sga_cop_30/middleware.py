import re
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.login_url = settings.LOGIN_URL
        self.exempt_urls = [re.compile(url) for url in settings.LOGIN_EXEMPT_URLS]

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        assert hasattr(request, 'user')
        
        # Se o usuário já está autenticado, não precisa fazer nada
        if request.user.is_authenticated:
            return None
            
        # Verifica se a URL atual está na lista de URLs isentas
        path = request.path_info.lstrip('/')
        
        # Verifica se a URL atual corresponde a alguma URL isenta
        for url_pattern in self.exempt_urls:
            if url_pattern.match(path):
                return None
                
        # Se chegou até aqui, o usuário não está autenticado e a URL não está isenta
        # Redireciona para a página de login com o parâmetro next
        login_url = reverse(settings.LOGIN_URL)
        return redirect(f"{login_url}?next={request.path}")
