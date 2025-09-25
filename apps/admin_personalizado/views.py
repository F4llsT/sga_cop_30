from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from apps.agenda.models import UserAgenda, Event
from apps.passefacil.models import ValidacaoQRCode

@staff_member_required
@login_required
def dashboard(request):
    User = get_user_model()

    # Métricas básicas
    total_users = User.objects.count()
    today = timezone.localdate()
    active_today = User.objects.filter(last_login__date=today).count()

    # Filtro de período (apenas para os favoritos/eventos)
    period = request.GET.get("period", "today")  # today | 7d | 30d
    now = timezone.now()
    if period == "7d":
        start_dt = now - timedelta(days=7)
        period_label = "Últimos 7 dias"
    elif period == "30d":
        start_dt = now - timedelta(days=30)
        period_label = "Últimos 30 dias"
    else:
        # today como padrão
        start_dt = now.replace(hour=0, minute=0, second=0, microsecond=0)
        period_label = "Hoje"

    # Agregação de favoritos por evento (usando UserAgenda)
    favoritos_qs = (
        UserAgenda.objects.filter(added_at__gte=start_dt)
        .values("event__id", "event__titulo")
        .annotate(total=Count("id"))
        .order_by("-total", "event__titulo")
    )

    # Extrair labels e valores para o gráfico
    eventos_labels = [row["event__titulo"] for row in favoritos_qs[:12]]
    eventos_values = [row["total"] for row in favoritos_qs[:12]]

    # Top event para o card de destaque
    top_event = eventos_labels[0] if eventos_labels else "—"

    # Passe Fácil: total de usos (validações válidas) no período selecionado
    passe_uses = ValidacaoQRCode.objects.filter(
        data_validacao__gte=start_dt,
        valido=True,
    ).count()

    # Dados de gráficos (exemplos funcionais; substitua quando tiver dados reais)
    if not eventos_labels:
        # Fallback amistoso quando não há dados
        eventos_labels = ["Sem dados"]
        eventos_values = [0]

    context = {
        "summary": {
            "total_users": total_users,
            "active_today": active_today,
            "top_event": top_event,
            "passe_uses": passe_uses,
        },
        "period": period,
        "period_label": period_label,
        "eventos_labels": eventos_labels,
        "eventos_values": eventos_values,
    }

    return render(request, 'admin_personalizado/dashboard/dashboard.html', context)