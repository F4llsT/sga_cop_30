#!/usr/bin/env python
import os
import django

# Configura o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sga_cop_30.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.notificacoes.models import Notificacao

User = get_user_model()

# Verifica usuários
users = User.objects.all()
print(f"Total de usuários: {users.count()}")

for user in users:
    print(f"Usuário: {user.email}")
    notificacoes = Notificacao.objects.filter(usuario=user)
    print(f"  - Total de notificações: {notificacoes.count()}")
    print(f"  - Não lidas: {notificacoes.filter(lida=False).count()}")
    print()
