from datetime import datetime, timedelta, timezone
from django.db import transaction

from zabbix_integration.models import ZabbixHost, ZabbixItem, ZabbixHistory, ZabbixEvent, ZabbixTrigger
from zabbix_integration.services.sync import get_client_for_cliente
from typing import Any


def _dt_from_epoch(epoch: str | int):
    return datetime.fromtimestamp(int(epoch), tz=timezone.utc)


@transaction.atomic
def sync_items(
    cliente_id: int,
    host: str,
    filtros: dict | None = None
) -> dict[str, Any]:
    """
    Sincroniza itens (item.get). Recomendação: filtrar por key para trazer só itens relevantes.
    """
    client = get_client_for_cliente(cliente_id)

    # Primeiro busca o hostid pelo nome técnico
    host_result = client.host_get(
        output=["hostid"],
        filter={"host": host}
    )
    print(f"Host encontrado: {host_result}")

    if not host_result:
        return {"error": "Host não encontrado no Zabbix"}

    hostid = host_result[0]["hostid"]
    print(f"HostID encontrado: {hostid}")
    params = {
        "output": ["itemid", 
                   "name", 
                   "key_", 
                   "value_type", 
                   "units", 
                   "delay", 
                   "lastvalue", 
                   "lastclock", 
                   "status",
                   ],
        "hostids": [hostid],
        #"limit": 1,
    }
    # 🔎 Aplicando filtros
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
    saved = 0
    for it in items:
        host = ZabbixHost.objects.filter(hostid=hostid).first()
        print(host)
        ZabbixItem.objects.update_or_create(
            cliente_id=cliente_id,
            itemid=it["itemid"],
            defaults={
                "host": host if host else None,
                "name": it.get("name") or "",
                "key": it.get("key_") or "",
                "value_type": int(it.get("value_type") or 0),
                "units": it.get("units"),
                "delay": it.get("delay"),
                "lastvalue": it.get("lastvalue"),
                "lastclock": _dt_from_epoch(it["lastclock"]) if it.get("lastclock") else None,
                "enabled": (it.get("status") == "0"),
            },
        )
        saved += 1

    return {
        "host": hostid,
        "total_encontrados": len(items),
        "salvos": saved,
        "filtros_aplicados": filtros or {}
    }


@transaction.atomic
def sync_events(
    cliente_id: int,
    triggerid: str,
    since_hours: int = 240,
    filtros: dict | None = None
) -> dict:

    client = get_client_for_cliente(cliente_id)

    # 🔎 Valida trigger local
    trigger_obj = ZabbixTrigger.objects.filter(
        cliente_id=cliente_id,
        triggerid=triggerid
    ).first()

    if not trigger_obj:
        return {"error": "Trigger não encontrada localmente. Execute sync_triggers primeiro."}

    # 🔎 Período
    time_from = int(
        (datetime.now(tz=timezone.utc) - timedelta(hours=since_hours)).timestamp()
    )

    params = {
        "source": 0,  # trigger events
        "object": 0,
        "objectids": [triggerid],
        "output": [
            "eventid",
            "clock",
            "value",
            "acknowledged",
            "severity",
            "name",
            "r_eventid",
            "c_eventid",
            "userid",
            "opdata",
            "objectid",
        ],
        "time_from": time_from,
        "sortfield": ["clock"],
        "sortorder": "DESC",
    }

    # 🔎 Aplicando filtros
    if filtros:
        filter_dict = {}

        if filtros.get("severity") is not None:
            filter_dict["severity"] = str(filtros["severity"])

        if filtros.get("acknowledged") is not None:
            filter_dict["acknowledged"] = str(filtros["acknowledged"])

        if filtros.get("value") is not None:
            filter_dict["value"] = str(filtros["value"])

        if filter_dict:
            params["filter"] = filter_dict

    events = client.event_get(**params)

    saved = 0

    for ev in events:
        ZabbixEvent.objects.update_or_create(
            cliente_id=cliente_id,
            eventid=str(ev["eventid"]),
            defaults={
                "trigger": trigger_obj,
                "name": ev.get("name"),
                "severity": int(ev.get("severity") or 0),
                "acknowledged": bool(int(ev.get("acknowledged") or 0)),
                "value": int(ev.get("value") or 0),
                "clock": _dt_from_epoch(ev["clock"]),
                "raw": ev,
                "r_eventid": ev.get("r_eventid"),
                "c_eventid": ev.get("c_eventid"),
                "opdata": ev.get("opdata"),
                "objectid": ev.get("objectid"),                
            },
        )
        saved += 1

    return {
        "trigger": triggerid,
        "total_encontrados": len(events),
        "salvos": saved,
        "filtros_aplicados": filtros or {},
    }

@transaction.atomic
def sync_history(cliente_id: int, itemids: list[str], time_from: datetime, time_till: datetime):
    """
    Sincroniza histórico (history.get) para uma lista de itemids em uma janela.
    OBS: history.get precisa do tipo (history=0/3/1/2/4) baseado em value_type.
    """
    client = get_client_for_cliente(cliente_id)

    items = list(ZabbixItem.objects.filter(cliente_id=cliente_id, itemid__in=itemids).select_related("host"))

    if not items:
        return

    # agrupamento por value_type (porque history.get exige o 'history' correto)
    by_type: dict[int, list[ZabbixItem]] = {}
    for it in items:
        by_type.setdefault(it.value_type, []).append(it)

    tf = int(time_from.replace(tzinfo=timezone.utc).timestamp())
    tt = int(time_till.replace(tzinfo=timezone.utc).timestamp())

    for value_type, typed_items in by_type.items():
        ids = [it.itemid for it in typed_items]

        rows = client.history_get(
            output="extend",
            history=value_type,  # 0 float, 1 char, 2 log, 3 uint, 4 text
            itemids=ids,
            time_from=tf,
            time_till=tt,
            sortfield="clock",
            sortorder="ASC",
            limit=50000,
        )

        # Mapa itemid -> item local
        local_item_map = {it.itemid: it for it in typed_items}

        # Bulk insert ignorando duplicados (mais rápido)
        to_create = []
        for r in rows:
            item = local_item_map.get(r["itemid"])
            if not item:
                continue
            to_create.append(
                ZabbixHistory(
                    cliente_id=cliente_id,
                    item=item,
                    clock=_dt_from_epoch(r["clock"]),
                    value=r.get("value"),
                )
            )

        # evita crash se vier muito grande (você pode chunkar depois)
        if to_create:
            ZabbixHistory.objects.bulk_create(to_create, ignore_conflicts=True, batch_size=2000)
