from datetime import datetime
from calendar import monthrange
from django.db.models import Avg
from zabbix_integration.models import ZabbixSLA


def _month_range(year: int, month: int):
    start = datetime(year, month, 1)
    last_day = monthrange(year, month)[1]
    end = datetime(year, month, last_day, 23, 59, 59)
    return start, end


def get_sla_summary(cliente_id: int, ano: int, mes: int) -> dict:
    start, end = _month_range(ano, mes)
    print(f"Calculando SLA para cliente_id={cliente_id} no período {start} a {end}")
    slas = (
        ZabbixSLA.objects
        .filter(
            cliente_id=cliente_id,
            effective_date__range=(start, end)   # 🔥 CORRIGIDO AQUI
        )
    )
    print(f"SLAs encontrados: {slas.count()}")
    if not slas.exists():
        return {"sla_geral": 0.0}

    # Se seu campo correto for "slo"
    sla_geral = slas.aggregate(media=Avg("slo"))["media"] or 0.0

    return {
        "sla_geral": round(sla_geral, 2)
    }