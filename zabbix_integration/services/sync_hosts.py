from zabbix_integration.models import ZabbixHost, ZabbixHostGroup
from .sync import get_client_for_cliente


def sync_hosts(cliente_id: int):
    print(f"Iniciando sincronização de hosts para cliente_id={cliente_id}")
    client = get_client_for_cliente(cliente_id)

    hosts = client.host_get(
        output=["hostid", "host", "name", "status"],
        selectGroups=["groupid", "name"]
    )

    for h in hosts:
        print(f"Sincronizando host: {h['host']} (ID: {h['hostid']})")
        host_obj, _ = ZabbixHost.objects.update_or_create(
            cliente_id=cliente_id,
            hostid=h["hostid"],
            defaults={
                "nome": h.get("name"),
                "status": h.get("status"),
                "raw": h
            }
        )

        # 🔥 Atualiza grupos do host
        grupos_relacionados = []

        for g in h.get("groups", []):
            group_obj, _ = ZabbixHostGroup.objects.update_or_create(
                cliente_id=cliente_id,
                groupid=g["groupid"],
                defaults={
                    "name": g["name"],
                    "raw": g
                }
            )
            grupos_relacionados.append(group_obj)

        # 🔥 Atualiza relação M2M (substitui completamente)
        host_obj.groups.set(grupos_relacionados)