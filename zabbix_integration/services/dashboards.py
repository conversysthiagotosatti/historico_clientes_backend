from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

from zabbix_integration.models import (
    ZabbixHost,
    ZabbixTrigger,
    ZabbixEvent,
)


def dashboard_executivo(cliente_id: int):

    now = timezone.now()
    last_24h = now - timedelta(hours=24)

    total_hosts = ZabbixHost.objects.filter(cliente_id=cliente_id).count()

    hosts_ativos = ZabbixHost.objects.filter(
        cliente_id=cliente_id,
        status=0
    ).count()

    triggers_ativas = ZabbixTrigger.objects.filter(
        cliente_id=cliente_id,
        value=1
    ).count()

    eventos_criticos = ZabbixEvent.objects.filter(
        cliente_id=cliente_id,
        severity__gte=4,
        clock__gte=last_24h
    ).count()

    top_hosts = (
        ZabbixEvent.objects
        .filter(cliente_id=cliente_id, clock__gte=last_24h)
        .values("trigger__items__host__hostname")
        .annotate(total=Count("id"))
        .order_by("-total")[:5]
    )

    return {
        "resumo": {
            "total_hosts": total_hosts,
            "hosts_ativos": hosts_ativos,
            "hosts_inativos": total_hosts - hosts_ativos,
            "triggers_ativas": triggers_ativas,
            "eventos_criticos_24h": eventos_criticos,
        },
        "top_hosts_problemas_24h": list(top_hosts),
    }