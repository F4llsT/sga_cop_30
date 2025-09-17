# apps/passefacil/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import PasseFacil
from django.utils import timezone
import qrcode
import io
import base64

@login_required
def passe_facil_view(request):
    try:
        passe = request.user.passe_facil
    except PasseFacil.DoesNotExist:
        passe = PasseFacil.objects.create(user=request.user)
    
    # Gerar QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(str(passe.codigo))
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Converter a imagem para base64
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    context = {
        'qr_code': qr_code_base64,
        'tempo_restante': passe.tempo_restante,
    }
    return render(request, 'passefacil/passe_facil.html', context)

@login_required
def atualizar_qr_code(request):
    if request.method == 'POST' and request.user.passe_facil:
        novo_codigo = request.user.passe_facil.gerar_novo_codigo()
        return JsonResponse({
            'status': 'success',
            'novo_codigo': str(novo_codigo),
            'tempo_restante': 60
        })
    return JsonResponse({'status': 'error'}, status=400)