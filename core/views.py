# In core/views.py
from django.shortcuts import render

# Add this function
def pagina_inicial(request):
    return render(request, 'pagina_inicial.html')