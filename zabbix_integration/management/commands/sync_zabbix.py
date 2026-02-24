import time
from django.core.management.base import BaseCommand
from django.utils import timezone

from zabbix_integration.services.sync_full import run_full_sync
from zabbix_integration.services.sync_incremental import run_incremental_sync
from clientes.models import Cliente


class Command(BaseCommand):
    help = "Executa sincronização Zabbix (full / incremental / ambos)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--cliente",
            type=int,
            help="ID do cliente específico"
        )

        parser.add_argument(
            "--tipo",
            type=str,
            choices=["full", "incremental", "ambos"],
            default="incremental",
            help="Tipo de sincronização"
        )

        parser.add_argument(
            "--todos",
            action="store_true",
            help="Executar para todos os clientes"
        )

    def handle(self, *args, **options):

        cliente_id = options.get("cliente")
        tipo = options.get("tipo")
        todos = options.get("todos")

        if not cliente_id and not todos:
            self.stdout.write(
                self.style.ERROR(
                    "Informe --cliente ID ou use --todos"
                )
            )
            return

        if todos:
            clientes = Cliente.objects.values_list("id", flat=True)
        else:
            clientes = [cliente_id]

        for cid in clientes:

            self.stdout.write(
                self.style.WARNING(
                    f"\n🚀 Iniciando sync cliente {cid} ({tipo})"
                )
            )

            inicio = time.time()

            if tipo == "full":
                run_full_sync(cid)

            elif tipo == "incremental":
                run_incremental_sync(cid)

            elif tipo == "ambos":
                run_full_sync(cid)
                run_incremental_sync(cid)

            duracao = round(time.time() - inicio, 2)

            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Cliente {cid} finalizado em {duracao}s"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"\n🏁 Sync finalizado às {timezone.now()}"
            )
        )