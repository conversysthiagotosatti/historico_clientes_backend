import logging
from celery import shared_task
from django.utils import timezone
from django.db import transaction

from zabbix_integration.services.sync_full import run_full_sync
from zabbix_integration.services.sync_incremental import run_incremental_sync
from zabbix_integration.models import ZabbixSyncControl


logger = logging.getLogger(__name__)


# -------------------------------------------------------
# 🔵 FULL SYNC TASK
# -------------------------------------------------------

@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5},
)
def full_sync_task(self, cliente_id: int):
    """
    Executa sincronização completa.
    Ideal rodar 1x por dia.
    """

    logger.info(f"[FULL SYNC] Iniciando cliente {cliente_id}")

    try:
        run_full_sync(cliente_id)

        logger.info(f"[FULL SYNC] Finalizado cliente {cliente_id}")

        return {
            "cliente_id": cliente_id,
            "status": "success",
            "finished_at": timezone.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"[FULL SYNC] Erro cliente {cliente_id}: {str(e)}")
        raise


# -------------------------------------------------------
# 🟢 INCREMENTAL SYNC TASK
# -------------------------------------------------------

@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 5},
)
def incremental_sync_task(self, cliente_id: int):
    """
    Executa sincronização incremental.
    Ideal rodar a cada 5 minutos.
    """

    logger.info(f"[INCREMENTAL SYNC] Iniciando cliente {cliente_id}")

    try:
        run_incremental_sync(cliente_id)

        logger.info(f"[INCREMENTAL SYNC] Finalizado cliente {cliente_id}")

        return {
            "cliente_id": cliente_id,
            "status": "success",
            "finished_at": timezone.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"[INCREMENTAL SYNC] Erro cliente {cliente_id}: {str(e)}")
        raise


# -------------------------------------------------------
# 🚀 FULL SYNC PARA TODOS CLIENTES
# -------------------------------------------------------

@shared_task
def full_sync_all_clients():
    """
    Dispara full sync para todos clientes.
    """

    from clientes.models import Cliente

    clientes = Cliente.objects.values_list("id", flat=True)

    for cliente_id in clientes:
        full_sync_task.delay(cliente_id)

    return {"total_clientes": len(clientes)}


# -------------------------------------------------------
# ⚡ INCREMENTAL PARA TODOS CLIENTES
# -------------------------------------------------------

@shared_task
def incremental_sync_all_clients():
    """
    Dispara incremental para todos clientes.
    """

    from clientes.models import Cliente

    clientes = Cliente.objects.values_list("id", flat=True)

    for cliente_id in clientes:
        incremental_sync_task.delay(cliente_id)

    return {"total_clientes": len(clientes)}