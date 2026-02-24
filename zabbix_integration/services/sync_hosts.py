from zabbix_integration.models import ZabbixHost
from zabbix_integration.services.sync import get_client_for_cliente


def sync_hosts_enterprise(cliente_id):
    client = get_client_for_cliente(cliente_id)

    hosts = client.host_get(output="extend")

    to_create = []
    existing = {
        h.hostid: h
        for h in ZabbixHost.objects.filter(cliente_id=cliente_id)
    }

    for h in hosts:
        hostid = str(h["hostid"])

        if hostid in existing:
            obj = existing[hostid]
            obj.hostname = h.get("host")
            obj.nome = h.get("name")
            obj.status = int(h.get("status") or 0)
            obj.raw = h
            obj.save()
        else:
            to_create.append(
                ZabbixHost(
                    cliente_id=cliente_id,
                    hostid=hostid,
                    hostname=h.get("host"),
                    nome=h.get("name"),
                    status=int(h.get("status") or 0),
                    raw=h,
                )
            )

    if to_create:
        ZabbixHost.objects.bulk_create(to_create, batch_size=500)