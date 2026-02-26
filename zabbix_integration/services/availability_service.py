from django.db.models import Avg
from zabbix_integration.models import ZabbixHost


def get_availability_summary(cliente_id: int, ano: int, mes: int) -> dict:
    """
    Considera que ZabbixHost possui campo disponibilidade_mes (% já calculado)
    """

    hosts = ZabbixHost.objects.filter(cliente_id=cliente_id)
    print(f"Hosts encontrados para cliente_id={cliente_id}: {hosts.count()}")
    if not hosts.exists():
        return {"media": 0.0}

    media = hosts.aggregate(media=Avg("disponibilidade_mes"))["media"] or 0.0
    print(f"Disponibilidade média calculada: {media}%")
    return {
        "media": round(media, 2)
    }