from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.core import views as core_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", core_views.pagina_inicial, name="home"),
    path("usuarios/", include("apps.usuarios.urls", namespace="usuarios")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("agenda/", include("apps.agenda.urls", namespace="agenda")),
]

# Only add static files in DEBUG mode
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)