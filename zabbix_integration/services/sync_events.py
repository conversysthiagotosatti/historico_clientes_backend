from datetime import datetime, timedelta, timezone
from zabbix_integration.models import ZabbixEvent, ZabbixTrigger
from zabbix_integration.services.sync import get_client_for_cliente
from .utils import dt_from_epoch


def sync_events_incremental(cliente_id, last_sync):
    client = get_client_for_cliente(cliente_id)

    if not last_sync:
        last_sync = datetime.now(tz=timezone.utc) - timedelta(hours=1)

    timestamp = int(last_sync.timestamp())

    events = client.event_get(
        source=0,
        object=0,
        time_from=timestamp,
        output="extend"
    )

    for ev in events:
        trigger = ZabbixTrigger.objects.filter(
            cliente_id=cliente_id,
            triggerid=ev.get("objectid")
        ).first()

        ZabbixEvent.objects.update_or_create(
            cliente_id=cliente_id,
            eventid=str(ev["eventid"]),
            defaults={
                "trigger": trigger,
                "severity": int(ev.get("severity") or 0),
                "acknowledged": bool(int(ev.get("acknowledged") or 0)),
                "clock": dt_from_epoch(ev.get("clock")),
                "raw": ev,
            }
        )