from .sync_events import sync_events_incremental
from .sync_control import (
    get_last_incremental,
    update_incremental_sync,
)


def run_incremental_sync(cliente_id):
    last_sync = get_last_incremental(cliente_id)

    sync_events_incremental(cliente_id, last_sync)

    update_incremental_sync(cliente_id)