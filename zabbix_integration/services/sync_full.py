from django.utils import timezone
from .sync_hosts import sync_hosts
from .sync_items import sync_items_enterprise
from .sync_triggers import sync_triggers_enterprise
from .sync_events import sync_events_incremental
from .sync_control import update_full_sync


def run_full_sync(cliente_id: int):
    #sync_hosts(cliente_id)
    #sync_items_enterprise(cliente_id)
    #sync_triggers_enterprise(cliente_id)
    sync_events_incremental(cliente_id)

    update_full_sync(cliente_id)