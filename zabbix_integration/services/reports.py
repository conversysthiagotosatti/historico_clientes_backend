from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from zabbix_integration.models import ZabbixEvent


def relatorio_incidentes(cliente_id: int, dias: int = 30):

    inicio = timezone.now() - timedelta(days=dias)

    eventos = ZabbixEvent.objects.filter(
        cliente_id=cliente_id,
        clock__gte=inicio
    )

    return {
        "periodo": f"Últimos {dias} dias",
        "total_eventos": eventos.count(),
        "por_severidade": list(
            eventos.values("severity")
            .annotate(total=Count("id"))
        ),
        "eventos_criticos": list(
            eventos.filter(severity__gte=4)
            .values("name", "clock", "severity")[:20]
        )
    }