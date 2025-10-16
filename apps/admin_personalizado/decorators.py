from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from functools import wraps

def superuser_required(view_func=None, redirect_url='admin_personalizado:acesso_negado'):
    """
    Decorator para views que verificam se o usuário é superusuário.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('admin_personalizado:login')
                
            if not request.user.is_superuser:
                if redirect_url:
                    return redirect(redirect_url)
                raise PermissionDenied
                
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    
    if view_func:
        return decorator(view_func)
    return decorator

def gerente_required(view_func=None, redirect_url='admin_personalizado:acesso_negado'):
    """
    Decorator para views que requerem privilégios de gerente ou superusuário.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('admin_personalizado:login')
                
            if not (request.user.role == 'GERENTE' or request.user.is_superuser):
                if redirect_url:
                    return redirect(redirect_url)
                raise PermissionDenied
                
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    
    if view_func:
        return decorator(view_func)
    return decorator

def eventos_required(view_func=None, redirect_url='admin_personalizado:acesso_negado'):
    """
    Decorator para views que requerem privilégios de usuário de eventos, gerente ou superusuário.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('admin_personalizado:login')
                
            if not (request.user.role in ['EVENTOS', 'GERENTE'] or request.user.is_superuser):
                if redirect_url:
                    return redirect(redirect_url)
                raise PermissionDenied
                
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    
    if view_func:
        return decorator(view_func)
    return decorator

def staff_required(view_func=None, redirect_url='admin_personalizado:acesso_negado'):
    """
    Decorator para views que requerem que o usuário seja staff.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('admin_personalizado:login')
                
            if not (request.user.is_staff or request.user.is_superuser):
                if redirect_url:
                    return redirect(redirect_url)
                raise PermissionDenied
                
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    
    if view_func:
        return decorator(view_func)
    return decorator
