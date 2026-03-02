from datetime import datetime
from calendar import monthrange
from django.db.models import Count
from zabbix_integration.models import ZabbixEvent


def _month_range(year: int, month: int):
    start = datetime(year, month, 1)
    last_day = monthrange(year, month)[1]
    end = datetime(year, month, last_day, 23, 59, 59)
    return start, end


def get_event_summary(cliente_id: int, ano: int, mes: int) -> dict:
    start, end = _month_range(ano, mes)

    eventos = ZabbixEvent.objects.filter(
        cliente_id=cliente_id,
        clock__range=(start, end)
    )

    total = eventos.count()

    criticos = eventos.filter(severity__gte=4).count()

    top_hosts = (
        eventos
        .values("host__name")
        .annotate(total=Count("id"))
        .order_by("-total")[:5]
    )

    top_hosts_formatado = [
        {"host": h["host__name"], "incidentes": h["total"]}
        for h in top_hosts
    ]

    return {
        "total": total,
        "criticos": criticos,
        "top_hosts": top_hosts_formatado
    }