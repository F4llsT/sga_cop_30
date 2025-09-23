from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from . import api_views

app_name = 'passefacil_api'

urlpatterns = [
    # Autenticação JWT
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API Passe Fácil
    path('validar-qr/', api_views.ValidarQRCodeAPIView.as_view(), name='validar_qr'),
    path('gerar-qr/', api_views.GerarQRCodeAPIView.as_view(), name='gerar_qr'),
    path('ultimas-validacoes/', api_views.UltimasValidacoesAPIView.as_view(), name='ultimas_validacoes'),
]
