from zabbix_integration.models import ZabbixTrigger, ZabbixItem
from zabbix_integration.services.sync import get_client_for_cliente
from .utils import dt_from_epoch


PAGE_SIZE = 1000


from .utils import chunked, dt_from_epoch

BATCH_ITEMS = 200


def sync_triggers_enterprise(cliente_id: int):

    print(f"Iniciando sincronização de triggers para cliente {cliente_id}")

    client = get_client_for_cliente(cliente_id)

    itemids = list(
        ZabbixItem.objects
        .filter(cliente_id=cliente_id)
        .values_list("itemid", flat=True)
    )

    total_processed = 0

    for item_chunk in chunked(itemids, BATCH_ITEMS):

        triggers = client.trigger_get(
            output=[
                "triggerid",
                "description",
                "priority",
                "status",
                "lastchange",
                "value",
                "expression",
            ],
            selectItems=["itemid"],
            itemids=item_chunk,   # 🔥 FILTRA POR ITEM
        )

        if not triggers:
            continue

        triggerids = [str(t["triggerid"]) for t in triggers]

        existing = {
            t.triggerid: t
            for t in ZabbixTrigger.objects.filter(
                cliente_id=cliente_id,
                triggerid__in=triggerids
            )
        }

        item_map = {
            i.itemid: i
            for i in ZabbixItem.objects.filter(
                cliente_id=cliente_id,
                itemid__in=item_chunk
            )
        }

        for trg in triggers:

            triggerid = str(trg["triggerid"])

            trigger_obj, _ = ZabbixTrigger.objects.update_or_create(
                cliente_id=cliente_id,
                triggerid=triggerid,
                defaults={
                    "name": trg.get("description"),
                    "description": trg.get("description"),
                    "expression": trg.get("expression"),
                    "priority": int(trg.get("priority") or 0),
                    "severity": int(trg.get("priority") or 0),
                    "value": int(trg.get("value") or 0),
                    "enabled": (trg.get("status") == "0"),
                    "status": (trg.get("status") == "0"),
                    "lastchange": dt_from_epoch(trg.get("lastchange")),
                    "raw": trg,
                }
            )

            # limpa relações antigas
            trigger_obj.items.clear()

            for item_data in trg.get("items", []):
                local_item = item_map.get(str(item_data["itemid"]))
                if local_item:
                    trigger_obj.items.add(local_item)

            total_processed += 1

        print(f"Triggers processadas até agora: {total_processed}")

    return {"total_triggers_processadas": total_processed}