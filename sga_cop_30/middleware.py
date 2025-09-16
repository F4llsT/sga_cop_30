import re
from django.conf import settings
from django.shortcuts import redirect

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Compile URL patterns once when the middleware is loaded
        self.exempt_urls = [re.compile(url) for url in settings.LOGIN_EXEMPT_URLS]

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        # Skip if user is already authenticated
        if hasattr(request, 'user') and request.user.is_authenticated:
            return None
            
        path = request.path_info.lstrip('/')
        
        # Check if the path matches any exempt URL pattern
        if any(url_pattern.match(path) for url_pattern in self.exempt_urls):
            return None
            
        # Redirect to login page with 'next' parameter
        from django.urls import reverse
        login_url = reverse('usuarios:login')
        return redirect(f"{login_url}?next={request.path}")