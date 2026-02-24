from django.utils import timezone
from zabbix_integration.models import ZabbixHost, ZabbixItem
from zabbix_integration.services.sync import get_client_for_cliente
from .utils import dt_from_epoch, chunked


BATCH_HOSTS = 10 #200
BATCH_DB = 2000


def sync_items_enterprise(cliente_id):
    client = get_client_for_cliente(cliente_id)

    hostids = list(
        ZabbixHost.objects
        .filter(cliente_id=cliente_id)
        .values_list("hostid", flat=True)
    )

    for host_chunk in chunked(hostids, BATCH_HOSTS):

        items = client.item_get(
            output="extend",
            hostids=host_chunk,
        )

        itemids = [str(it["itemid"]) for it in items]

        existing = {
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
            host = host_map.get(str(it["hostid"]))

            if not host:
                continue

            if itemid in existing:
                obj = existing[itemid]
                obj.name = it.get("name")
                obj.lastvalue = it.get("lastvalue")
                obj.lastclock = dt_from_epoch(it.get("lastclock"))
                to_update.append(obj)
            else:
                to_create.append(
                    ZabbixItem(
                        cliente_id=cliente_id,
                        itemid=itemid,
                        host=host,
                        name=it.get("name"),
                        key=it.get("key_"),
                        value_type=int(it.get("value_type") or 0),
                        units=it.get("units"),
                        delay=it.get("delay"),
                        lastvalue=it.get("lastvalue"),
                        lastclock=dt_from_epoch(it.get("lastclock")),
                        enabled=(it.get("status") == "0"),
                        raw=it,
                    )
                )

        if to_create:
            ZabbixItem.objects.bulk_create(to_create, batch_size=BATCH_DB)

        if to_update:
            ZabbixItem.objects.bulk_update(
                to_update,
                ["name", "lastvalue", "lastclock"],
                batch_size=BATCH_DB
            )