from datetime import datetime
from calendar import monthrange
from django.db.models import Q
from zabbix_integration.models import ZabbixEvent


def _month_range(year: int, month: int):
    start = datetime(year, month, 1)
    last_day = monthrange(year, month)[1]
    end = datetime(year, month, last_day, 23, 59, 59)
    return start, end


def get_mttr(cliente_id: int, ano: int, mes: int) -> float:
    start, end = _month_range(ano, mes)

    eventos = ZabbixEvent.objects.filter(
        cliente_id=cliente_id,
        clock__range=(start, end)
    ).order_by("eventid", "clock")

    mttrs = []
    problemas = {}

    for ev in eventos:
        if ev.value == 1:
            problemas[ev.eventid] = ev.clock

        elif ev.value == 0 and ev.eventid in problemas:
            inicio = problemas.pop(ev.eventid)
            duracao = (ev.clock - inicio).total_seconds() / 60
            mttrs.append(duracao)

    if not mttrs:
        return 0.0

    return round(sum(mttrs) / len(mttrs), 2)