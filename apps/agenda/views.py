from django.shortcuts import render
from django.http import HttpResponse # <-- ESTA LINHA É A CORREÇÃO

# 2. Crie suas views (funções) aqui

def pagina_inicial(request):
    """
    Esta função é chamada quando um usuário acessa a página inicial.
    Ela retorna um objeto HttpResponse.
    """
    # 3. Use a ferramenta importada para retornar o conteúdo
    return HttpResponse("<h1>Bem-vindo!</h1><p>Seu projeto Django está no ar.</p>")

