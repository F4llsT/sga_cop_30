from django.urls import path
from . import views # Importa as views do app 'usuarios'

# O namespace definido no urls.py principal se aplica a este arquivo.
app_name = 'agenda'

urlpatterns = [
    # Adicione suas URLs para o app 'usuarios' aqui.
    # Exemplo: path('login/', views.login_view, name='login'),
]
