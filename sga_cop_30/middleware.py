import re
from django.conf import settings
from django.shortcuts import redirect

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

def process_view(self, request, view_func, view_args, view_kwargs):
    if not hasattr(request, 'user'):
        return None
        
    if request.user.is_authenticated:
        return None
        
    path = request.path_info.lstrip('/')
    exempt_urls = [re.compile(url) for url in settings.LOGIN_EXEMPT_URLS]
    
    for url_pattern in exempt_urls:
        if url_pattern.match(path):
            return None
            
    # Corrigindo o redirecionamento para usar o namespace correto
    from django.urls import reverse
    login_url = reverse('usuarios:login')  # Usando o namespace 'usuarios'
    return redirect(f"{login_url}?next={request.path}")