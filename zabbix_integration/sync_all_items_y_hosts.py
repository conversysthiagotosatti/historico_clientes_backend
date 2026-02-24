from django.db import transaction
from django.utils import timezone
from typing import Any
from zabbix_integration.models import ZabbixHost, ZabbixItem
from zabbix_integration.services.sync import get_client_for_cliente


BATCH_HOSTS = 200
BATCH_DB = 2000


def chunked(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]


def sync_items_enterprise(cliente_id: int) -> dict[str, Any]:
    """
    Sincronização otimizada para 1000+ hosts.
    """

    client = get_client_for_cliente(cliente_id)

    hostids = list(
        ZabbixHost.objects
        .filter(cliente_id=cliente_id)
        .values_list("hostid", flat=True)
    )

    total_hosts = len(hostids)
    total_items = 0
    total_created = 0
    total_updated = 0

    for host_chunk in chunked(hostids, BATCH_HOSTS):

        items = client.item_get(
            output=[
                "itemid",
                "hostid",
                "name",
                "key_",
                "value_type",
                "units",
                "delay",
                "lastvalue",
                "lastclock",
                "status",
            ],
            hostids=host_chunk,
        )

        total_items += len(items)

        itemids = [str(it["itemid"]) for it in items]

        existing_items = {
            obj.itemid: obj
            for obj in ZabbixItem.objects.filter(
                cliente_id=cliente_id,
                itemid__in=itemids
            )
        }

        host_map = {
            h.hostid: h
            for h in ZabbixHost.objects.filter(
                cliente_id=cliente_id,
                hostid__in=host_chunk
            )
        }

        to_create = []
        to_update = []

        for it in items:
            itemid = str(it["itemid"])
            host_obj = host_map.get(str(it["hostid"]))

            if not host_obj:
                continue

            if itemid in existing_items:
                obj = existing_items[itemid]
                obj.name = it.get("name") or ""
                obj.key = it.get("key_") or ""
                obj.value_type = int(it.get("value_type") or 0)
                obj.units = it.get("units")
                obj.delay = it.get("delay")
                obj.lastvalue = it.get("lastvalue")
                obj.lastclock = (
                    timezone.datetime.fromtimestamp(
                        int(it["lastclock"]), tz=timezone.utc
                    )
                    if it.get("lastclock")
                    else None
                )
                obj.enabled = (it.get("status") == "0")
                to_update.append(obj)
            else:
                to_create.append(
                    ZabbixItem(
                        cliente_id=cliente_id,
                        itemid=itemid,
                        host=host_obj,
                        name=it.get("name") or "",
                        key=it.get("key_") or "",
                        value_type=int(it.get("value_type") or 0),
                        units=it.get("units"),
                        delay=it.get("delay"),
                        lastvalue=it.get("lastvalue"),
                        lastclock=(
                            timezone.datetime.fromtimestamp(
                                int(it["lastclock"]), tz=timezone.utc
                            )
                            if it.get("lastclock")
                            else None
                        ),
                        enabled=(it.get("status") == "0"),
                        raw=it,
                    )
                )

        if to_create:
            ZabbixItem.objects.bulk_create(
                to_create,
                batch_size=BATCH_DB,
                ignore_conflicts=True
            )
            total_created += len(to_create)

        if to_update:
            ZabbixItem.objects.bulk_update(
                to_update,
                [
                    "name",
                    "key",
                    "value_type",
                    "units",
                    "delay",
                    "lastvalue",
                    "lastclock",
                    "enabled",
                ],
                batch_size=BATCH_DB,
            )
            total_updated += len(to_update)

    return {
        "hosts_processados": total_hosts,
        "itens_encontrados": total_items,
        "itens_criados": total_created,
        "itens_atualizados": total_updated,
    }