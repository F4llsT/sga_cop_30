import os
import sys
from django.core.wsgi import get_wsgi_application

# Adiciona o diretório do projeto ao path
path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if path not in sys.path:
    sys.path.append(path)

# Define o módulo de configurações do Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sga_cop_30.settings')

# Configura o aplicativo WSGI
django_app = get_wsgi_application()

# Adiciona o WhiteNoise para servir arquivos estáticos
from whitenoise import WhiteNoise
application = WhiteNoise(django_app, root=os.path.join(path, 'staticfiles'))
application.add_files(os.path.join(path, 'media'), prefix='media/')
