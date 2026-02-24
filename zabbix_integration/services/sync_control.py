from django.utils import timezone
from zabbix_integration.models import ZabbixSyncControl


def get_or_create_control(cliente_id):
    return ZabbixSyncControl.objects.get_or_create(cliente_id=cliente_id)[0]


def update_full_sync(cliente_id):
    control = get_or_create_control(cliente_id)
    control.last_full_sync = timezone.now()
    control.save()


def update_incremental_sync(cliente_id):
    control = get_or_create_control(cliente_id)
    control.last_incremental_sync = timezone.now()
    control.save()


def get_last_incremental(cliente_id):
    control = get_or_create_control(cliente_id)
    return control.last_incremental_sync