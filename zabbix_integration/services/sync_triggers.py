from zabbix_integration.models import ZabbixTrigger
from zabbix_integration.services.sync import get_client_for_cliente
from .utils import dt_from_epoch


def sync_triggers_enterprise(cliente_id):
    client = get_client_for_cliente(cliente_id)

    triggers = client.trigger_get(output="extend", selectItems=["itemid"])

    for trg in triggers:
        trigger_obj, _ = ZabbixTrigger.objects.update_or_create(
            cliente_id=cliente_id,
            triggerid=str(trg["triggerid"]),
            defaults={
                "description": trg.get("description"),
                "priority": int(trg.get("priority") or 0),
                "status": trg.get("status") == "0",
                "lastchange": dt_from_epoch(trg.get("lastchange")),
                "raw": trg,
            }
        )