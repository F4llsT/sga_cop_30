from django.contrib import admin
from django.urls import path, include
from core import views as core_views # 1. Adicione esta importação

urlpatterns = [
    path('admin/', admin.site.urls),
    path('contas/', include('usuarios.urls')),
    
    # 2. Adicione esta linha para a página inicial
    path('', core_views.pagina_inicial, name='home'), 
]