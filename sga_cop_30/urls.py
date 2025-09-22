from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.core import views as core_views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

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
    
    # API Passe Fácil
    path('api/passefacil/', include('apps.passefacil.api_urls', namespace='passefacil_api')),
    
    # API Auth JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

# Servir arquivos estáticos em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)