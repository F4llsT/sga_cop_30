from django.shortcuts import render

# Create your views here.
def pagina_inicial(request):
    return HttpResponse("<h1>Bem-vindo!</h1><p>Seu projeto Django está no ar.</p>")
