from django.contrib import admin
from django.urls import path, include
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
]
