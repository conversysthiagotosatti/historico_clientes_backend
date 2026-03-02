from datetime import datetime, timedelta, timezone
from zabbix_integration.models import ZabbixEvent, ZabbixTrigger
from zabbix_integration.services.sync import get_client_for_cliente
from .utils import chunked, dt_from_epoch


BATCH_TRIGGERS = 200


def sync_events_incremental(cliente_id: int, last_sync=None):

    print(f"Iniciando sync de eventos cliente {cliente_id}")

    client = get_client_for_cliente(cliente_id)

    if not last_sync:
        last_sync = datetime.now(tz=timezone.utc) - timedelta(hours=720)

    timestamp = int(last_sync.timestamp())

    triggerids = list(
        ZabbixTrigger.objects
        .filter(cliente_id=cliente_id)
        .values_list("triggerid", flat=True)
    )

    total_events = 0
    print(chunked(triggerids, BATCH_TRIGGERS))
    for trigger_chunk in chunked(triggerids, BATCH_TRIGGERS):
        print(f"Processando chunk de triggers: {trigger_chunk}")
        events = client.event_get(
            source=0,
            object=0,
            objectids=trigger_chunk,  # 🔥 FILTRA POR TRIGGER
            time_from=timestamp,
            output=[
                "eventid",
                "objectid",
                "clock",
                "value",
                "acknowledged",
                "severity",
                "name",
                "objectid",
            ],
            sortfield="clock",
            sortorder="ASC",
        )

        if not events:
            continue

        trigger_map = {
            t.triggerid: t
            for t in ZabbixTrigger.objects.filter(
                cliente_id=cliente_id,
                triggerid__in=trigger_chunk
            )
        }

        for ev in events:

            trigger = trigger_map.get(str(ev["objectid"]))

            ZabbixEvent.objects.update_or_create(
                cliente_id=cliente_id,
                eventid=str(ev["eventid"]),
                defaults={
                    "trigger": trigger,
                    "name": ev.get("name"),
                    "severity": int(ev.get("severity") or 0),
                    "acknowledged": bool(int(ev.get("acknowledged") or 0)),
                    "value": int(ev.get("value") or 0),
                    "clock": dt_from_epoch(ev.get("clock")),
                    "raw": ev,
                    "objectid": str(ev.get("objectid")),
                },
            )

        total_events += len(events)

        print(f"Eventos processados até agora: {total_events}")

    return {"total_eventos_processados": total_events}