from zabbix_integration.models import ZabbixHostGroup
from .sync import get_client_for_cliente


def sync_hostgroups(cliente_id: int) -> dict:
    client = get_client_for_cliente(cliente_id)

    groups = client.hostgroup_get(
        output=["groupid", "name"],
        sortfield="name"
    )

    total = 0

    for g in groups:
        ZabbixHostGroup.objects.update_or_create(
            cliente_id=cliente_id,
            groupid=g["groupid"],
            defaults={
                "name": g["name"],
                "raw": g
            }
        )
        total += 1

    return {
        "cliente_id": cliente_id,
        "groups_sincronizados": total
    }