from django.db import transaction
from typing import Any
from zabbix_integration.models import ZabbixHost, ZabbixItem
from zabbix_integration.services.sync import get_client_for_cliente
from datetime import datetime, timedelta, timezone as dt_timezone

def _dt_from_epoch(ts: str | int):
    return datetime.fromtimestamp(int(ts), tz=dt_timezone.utc)

@transaction.atomic
def sync_all_items_by_hosts(
    cliente_id: int,
    filtros: dict | None = None
) -> dict[str, Any]:
    """
    Percorre todos os hosts locais e sincroniza os itens via API.
    """

    client = get_client_for_cliente(cliente_id)

    hosts = ZabbixHost.objects.filter(cliente_id=cliente_id)

    total_hosts = hosts.count()
    total_items = 0
    total_saved = 0

    for host in hosts:

        params = {
            "output": [
                "itemid",
                "name",
                "key_",
                "value_type",
                "units",
                "delay",
                "lastvalue",
                "lastclock",
                "status",
            ],
            "hostids": [host.hostid],
        }

        # 🔎 Aplicando filtros se existirem
        if filtros:
            filter_dict = {}
            search_dict = {}

            if filtros.get("status") is not None:
                filter_dict["status"] = str(filtros["status"])

            if filtros.get("key_"):
                search_dict["key_"] = filtros["key_"]

            if filtros.get("name"):
                search_dict["name"] = filtros["name"]

            if filter_dict:
                params["filter"] = filter_dict

            if search_dict:
                params["search"] = search_dict
                params["searchWildcardsEnabled"] = True

        items = client.item_get(**params)

        total_items += len(items)

        for it in items:
            ZabbixItem.objects.update_or_create(
                cliente_id=cliente_id,
                itemid=str(it["itemid"]),
                defaults={
                    "host": host,
                    "name": it.get("name") or "",
                    "key": it.get("key_") or "",
                    "value_type": int(it.get("value_type") or 0),
                    "units": it.get("units"),
                    "delay": it.get("delay"),
                    "lastvalue": it.get("lastvalue"),
                    "lastclock": _dt_from_epoch(it["lastclock"]) if it.get("lastclock") else None,
                    "enabled": (it.get("status") == "0"),
                    "raw": it,
                },
            )
            total_saved += 1

    return {
        "hosts_processados": total_hosts,
        "itens_encontrados": total_items,
        "itens_salvos": total_saved,
        "filtros_aplicados": filtros or {},
    }