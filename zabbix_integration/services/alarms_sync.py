from datetime import datetime, timedelta, timezone
from django.db import transaction

from zabbix_integration.services.sync import get_client_for_cliente
from zabbix_integration.models import ZabbixAlarm, ZabbixAlarmEvent, ZabbixAlertSent

from django.utils.dateparse import parse_datetime


def _dt(epoch: str | int) -> datetime:
    return datetime.fromtimestamp(int(epoch), tz=timezone.utc)

@transaction.atomic
def sync_active_alarms(
    cliente_id: int,
    since_hours: int | None = None,
    data_inicio: str | None = None,
    data_fim: str | None = None,
) -> dict:
    """
    Captura alarmes ATIVOS (problem.get) filtrando por intervalo de datas.
    """

    client = get_client_for_cliente(cliente_id)

    # -------------------------------------------------
    # 🎯 Define período
    # -------------------------------------------------
    print(f"data de inicio: {data_inicio}, data de fim: {data_fim}, since_hours: {since_hours}")
    if data_inicio and data_fim:
        dt_inicio = parse_datetime(data_inicio)
        dt_fim = parse_datetime(data_fim)

        if not dt_inicio or not dt_fim:
            raise ValueError("Formato inválido. Use ISO: 2026-02-01T00:00:00")

        dt_inicio = dt_inicio.astimezone(timezone.utc)
        dt_fim = dt_fim.astimezone(timezone.utc)

        time_from = int(dt_inicio.timestamp())
        time_till = int(dt_fim.timestamp())
        print(f"🔎 Buscando alarmes entre as datas {dt_inicio} e {dt_fim}")

    elif since_hours:
        dt_inicio = datetime.now(tz=timezone.utc) - timedelta(hours=since_hours)
        time_from = int(dt_inicio.timestamp())
        time_till = int(datetime.now(tz=timezone.utc).timestamp())
    else:
        raise ValueError("Informe since_hours ou data_inicio/data_fim")

    print(f"🔎 Buscando alarmes entre timestamp {time_from} e {time_till}")

    # -------------------------------------------------
    # 📡 Consulta no Zabbix
    # -------------------------------------------------
    problems = client.problem_get(
        output="extend",
        time_from=time_from,
        time_till=time_till,
        sortfield=["eventid"],
        sortorder="DESC",
        selectHosts=["hostid", "name"],
        selectTags="extend",
    ) or []

    upserts = 0
    results = []

    for p in problems:
        hosts = p.get("hosts") or []

        # se vier mais de um host, pega o primeiro
        hostid = None
        hostname = None

        if hosts:
            hostid = str(hosts[0].get("hostid"))
            hostname = hosts[0].get("name")

        ZabbixAlarm.objects.update_or_create(
            cliente_id=cliente_id,
            eventid=str(p["eventid"]),
            defaults={
                "name": p.get("name") or "",
                "severity": int(p.get("severity") or 0),
                "acknowledged": bool(int(p.get("acknowledged") or 0)),
                "clock": _dt(p["clock"]),
                "hostid": hostid,
                "hostname": hostname,
                "raw": p,
            },
        )

        upserts += 1

    return {
        "cliente_id": cliente_id,
        "periodo": {
            "time_from": time_from,
            "time_till": time_till,
        },
        "total": upserts,
        "alarms": results,
    }

def _resolve_periodo(since_hours=None, data_inicio=None, data_fim=None):
    if data_inicio and data_fim:
        dt_inicio = parse_datetime(data_inicio)
        dt_fim = parse_datetime(data_fim)
        if not dt_inicio or not dt_fim:
            raise ValueError("Formato inválido. Use ISO: 2026-02-01T00:00:00")

        dt_inicio = dt_inicio.astimezone(timezone.utc)
        dt_fim = dt_fim.astimezone(timezone.utc)
        return int(dt_inicio.timestamp()), int(dt_fim.timestamp())

    if since_hours:
        dt_inicio = datetime.now(tz=timezone.utc) - timedelta(hours=since_hours)
        dt_fim = datetime.now(tz=timezone.utc)
        return int(dt_inicio.timestamp()), int(dt_fim.timestamp())

    raise ValueError("Informe since_hours ou data_inicio/data_fim")


@transaction.atomic
def sync_alarm_events(
    cliente_id: int,
    since_hours: int | None = None,
    data_inicio: str | None = None,
    data_fim: str | None = None,
    limit: int = 2000,
) -> dict:
    """
    Captura eventos (event.get) e GRAVA no banco.
    """
    client = get_client_for_cliente(cliente_id)
    time_from, time_till = _resolve_periodo(since_hours, data_inicio, data_fim)

    # ✅ inclua objectid (triggerid) para mapear host
    params = {
        "output": ["eventid", "clock", "value", "name", "severity", "acknowledged", "objectid"],
        "time_from": time_from,
        "time_till": time_till,
        "source": 0,  # trigger events
        "object": 0,  # trigger
        "sortfield": ["eventid"],
        "sortorder": "DESC",
        "limit": limit,
        # ⚠️ remova selectHosts se seu Zabbix estiver retornando 500
        # "selectHosts": ["hostid", "name"],
    }

    events = client._call("event.get", params) or []

    # ---- resolve host via trigger.get (porque event.get nem sempre traz hosts)
    trigger_ids = list({str(e.get("objectid")) for e in events if e.get("objectid")})
    trigger_host_map: dict[str, dict] = {}

    if trigger_ids:
        triggers = client._call("trigger.get", {
            "output": ["triggerid"],
            "triggerids": trigger_ids,
            "selectHosts": ["hostid", "name"],
        }) or []

        for t in triggers:
            hosts = t.get("hosts") or []
            if hosts:
                trigger_host_map[str(t.get("triggerid"))] = {
                    "hostid": str(hosts[0].get("hostid")),
                    "hostname": hosts[0].get("name"),
                }

    upserts = 0
    for e in events:
        triggerid = str(e.get("objectid")) if e.get("objectid") else None
        host_data = trigger_host_map.get(triggerid or "", {})

        ZabbixAlarmEvent.objects.update_or_create(
            cliente_id=cliente_id,
            eventid=str(e.get("eventid")),
            defaults={
                "clock": _dt(e.get("clock")),
                "name": e.get("name") or "",
                "severity": int(e.get("severity") or 0),
                "acknowledged": bool(int(e.get("acknowledged") or 0)),
                #"value": int(e.get("value") or 0),
                #"triggerid": triggerid,
                "hostid": host_data.get("hostid"),
                "hostname": host_data.get("hostname"),
                "raw": e,
            },
        )
        upserts += 1

    return {
        "cliente_id": cliente_id,
        "periodo": {"time_from": time_from, "time_till": time_till},
        "total_recebido": len(events),
        "gravados": upserts,
    }

@transaction.atomic
def sync_alerts_sent(cliente_id: int, since_hours: int = 24, limit: int = 2000,) -> dict:
    """
    (Opcional) Captura alertas ENVIADOS (alert.get).
    """
    client = get_client_for_cliente(cliente_id)
    time_from = int((datetime.now(tz=timezone.utc) - timedelta(hours=since_hours)).timestamp())

    alerts = client.alert_get(
        output="extend",
        time_from=time_from,
        sortfield="clock",
        sortorder="DESC",
        limit=limit,
    ) or []

    created = 0
    for a in alerts:
        obj, was_created = ZabbixAlertSent.objects.update_or_create(
            alertid=str(a["alertid"]),
            defaults={
                "cliente_id": cliente_id,
                "eventid": str(a.get("eventid")) if a.get("eventid") else None,
                "clock": _dt(a["clock"]),
                "sendto": a.get("sendto"),
                "subject": a.get("subject"),
                "message": a.get("message"),
                "status": int(a.get("status") or 0) if a.get("status") is not None else None,
                "raw": a,
            },
        )
        if was_created:
            created += 1

    return {"synced_alerts": len(alerts), "new_alerts": created, "since_hours": since_hours}
