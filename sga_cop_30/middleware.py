import re
from django.conf import settings
from django.shortcuts import redirect
from django.urls import resolve, reverse
from django.http import HttpResponseRedirect

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
            
        # Skip for admin URLs
        if path.startswith('admin/'):
            return None
            
        # Skip for static files
        if path.startswith(settings.STATIC_URL.lstrip('/')):
            return None
            
        # Skip for media files
        if hasattr(settings, 'MEDIA_URL') and path.startswith(settings.MEDIA_URL.lstrip('/')):
            return None
            
        # Get the resolved URL name
        try:
            resolved = resolve(request.path_info)
            # Skip if the view is in an exempt app
            if hasattr(resolved, 'app_name') and resolved.app_name in settings.LOGIN_EXEMPT_APPS:
                return None
        except:
            pass
            
        # Build the login URL with next parameter
        login_url = reverse('usuarios:login')
        redirect_url = f"{login_url}?next={request.path}"
        
        # Avoid redirect loops
        if request.path != redirect_url:
            return HttpResponseRedirect(redirect_url)
            
        return None