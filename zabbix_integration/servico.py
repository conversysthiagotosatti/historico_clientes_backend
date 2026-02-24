from __future__ import annotations

from typing import Any

from zabbix_integration.services.sync import get_client_for_cliente
from .models import ZabbixHost, ZabbixItem, ZabbixTrigger, ZabbixEvent
from datetime import datetime, timedelta, timezone as dt_timezone
from django.db import transaction

def sync_hosts(
    cliente_id: int,
    client,
    filtros: dict | None = None
) -> dict[str, Any]:

    params = {
        "output": ["hostid", 
                   "host", 
                   "name", 
                   "status", 
                   "description",
                   "proxy_hostid",
                   "maintenance_status",
                   "maintenace_type",
                   "available",
                   "snmp_available",
                   "ipmi_available",
                   "jmx_available",
                   "tls_connect",
                   "tls_accept",
                   "flags",
                   "inventory_mode",
                   ],
        "selectInterfaces": ["ip", "dns", "port"],
    }

    # ✅ Aplicando filtros se existirem
    if filtros:
        filter_dict = {}
        search_dict = {}

        if filtros.get("host"):
            filter_dict["host"] = filtros["host"]

        if filtros.get("hostname"):
            # busca parcial no name
            search_dict["name"] = filtros["hostname"]

        if filter_dict:
            params["filter"] = filter_dict

        if search_dict:
            params["search"] = search_dict
            params["searchWildcardsEnabled"] = True

    # 🔹 chamada ao Zabbix
    result = client.host_get(**params)

    saved = 0

    for h in result:
        interfaces = h.get("interfaces") or []
        i0 = interfaces[0] if interfaces else {}

        defaults = {
            "hostid": h.get("hostid"),
            "hostname": h.get("host"),
            "nome": h.get("name"),
            "status": int(h.get("status") or 0),
            "raw": h,
        }

        # ⚠️ Mantive sua estrutura atual sem quebrar
        ZabbixHost.objects.update_or_create(
            cliente_id=cliente_id,
            hostid=str(h["hostid"]),
            defaults=defaults,  # 🔥 Recomendo usar defaults
        )

        saved += 1

    return {
        "count": len(result),
        "saved": saved,
        "filtros_aplicados": filtros or {}
    }


def _dt_from_epoch(ts: str | int):
    return datetime.fromtimestamp(int(ts), tz=dt_timezone.utc)



@transaction.atomic
def sync_triggers(
    cliente_id: int,
    item_key: str,
    filtros: dict | None = None
) -> dict:

    client = get_client_for_cliente(cliente_id)

    # 🔎 Buscar item local pelo key
    item_obj = ZabbixItem.objects.filter(
        cliente_id=cliente_id,
        key=item_key
    ).select_related("host").first()

    if not item_obj:
        return {"error": "Item não encontrado localmente. Execute sync_items primeiro."}

    # 🔎 Buscar trigger via itemid
    params = {
        "output": [
            "triggerid",
            "description",
            "expression",
            "priority",
            "status",
            "value",
            "lastchange"
        ],
        "selectHosts": ["hostid", "host"],
        "selectItems": ["itemid", "name", "key_"],
    }

    # 🔎 Filtro por item
    params["itemids"] = [item_obj.itemid]

    # 🔎 Aplicando filtros
    if filtros:
        filter_dict = {}
        search_dict = {}

        if filtros.get("priority") is not None:
            filter_dict["priority"] = str(filtros["priority"])

        if filtros.get("status") is not None:
            filter_dict["status"] = str(filtros["status"])

        if filtros.get("description"):
            search_dict["description"] = filtros["description"]

        if filter_dict:
            params["filter"] = filter_dict

        if search_dict:
            params["search"] = search_dict
            params["searchWildcardsEnabled"] = True

    triggers = client.trigger_get(**params)

    saved = 0

    for trg in triggers:
        ZabbixTrigger.objects.update_or_create(
            cliente_id=cliente_id,
            triggerid=str(trg["triggerid"]),
            defaults={
                "description": trg.get("description"),
                "expression": trg.get("expression"),
                "priority": int(trg.get("priority") or 0),
                "status": (trg.get("status") == "0"),
                "value": int(trg.get("value") or 0),
                "lastchange": _dt_from_epoch(trg["lastchange"]) if trg.get("lastchange") else None,
                "raw": trg,
                "items": item_obj,
            }
        )
        saved += 1

    return {
        "item": item_key,
        "host": item_obj.host.hostname if item_obj.host else None,
        "total_encontrados": len(triggers),
        "salvos": saved,
        "filtros_aplicados": filtros or {}
    }

def sync_events(cliente_id: int, since_hours: int = 24):
    client = get_client_for_cliente(cliente_id)

    time_from = int((datetime.now(tz=dt_timezone.utc) - timedelta(hours=since_hours)).timestamp())

    events = client.event_get(
        output=["eventid", "clock", "value", "name", "severity", "acknowledged", "objectid"],
        source=0,  # ✅ trigger events
        object=148958,  # ✅ trigger
        #objectids=["148958", "138328"],
        time_from=time_from,
        sortfield=["clock"],
        sortorder="DESC",
        limit=2000,
    )

    # mapas locais
    local_triggers = {
        t.triggerid: t
        for t in ZabbixTrigger.objects.filter(cliente_id=cliente_id)
    }
    local_hosts = {
        str(h.hostid): h
        for h in ZabbixHost.objects.filter(cliente_id=cliente_id)
    }

    # Para ligar host ao evento: pega o host principal da trigger (ou nenhum)
    for ev in events:
        trig_id = str(ev.get("objectid") or "")
        trig = local_triggers.get(trig_id)

        host = None
        if trig:
            # se M2M: escolha o primeiro host como "principal" pro evento
            first = trig.hosts.first()
            host = first

        ZabbixEvent.objects.update_or_create(
            eventid=str(ev["eventid"]),
            defaults={
                "cliente_id": cliente_id,
                "trigger": trig,
                "host": host,
                "name": ev.get("name"),
                "severity": int(ev.get("severity") or 0),
                "value": int(ev.get("value") or 0),
                "acknowledged": bool(int(ev.get("acknowledged") or 0)),
                "clock": _dt_from_epoch(ev["clock"]),
                "raw": ev,
            },
        )