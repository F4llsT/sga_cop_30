from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.core import views as core_views

urlpatterns = [
    path("admin/", admin.site.urls),

    # Página inicial
    path("", core_views.pagina_inicial, name="home"),

    # Autenticação customizada (do app usuarios)
    path("usuarios/", include("apps.usuarios.urls", namespace="usuarios")),

    # Autenticação padrão do Django (/accounts/login etc.)
    path("accounts/", include("django.contrib.auth.urls")),

    # Agenda (corrigido para ter o namespace)
    path("agenda/", include("apps.agenda.urls", namespace="agenda")),
    
    # Notificações
    path("notificacoes/", include("apps.notificacoes.urls", namespace="notificacoes")),
    
    # Passe Fácil
    path('passefacil/', include('apps.passefacil.urls', namespace='passefacil')),
]

# Servir arquivos estáticos em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)