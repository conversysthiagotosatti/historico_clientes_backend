from django.core.management.base import BaseCommand

from helpdesk.models import Departamento
from softdesk.services.departamento_service import DepartamentoSoftdeskService


class Command(BaseCommand):
    help = "Sincroniza departamentos da API Softdesk para a tabela helpdesk.Departamento."

    def add_arguments(self, parser):
        parser.add_argument(
            "cliente_id",
            type=int,
            help="ID do cliente usado para buscar os parâmetros do Softdesk.",
        )

    def handle(self, *args, **options):
        cliente_id = options["cliente_id"]

        departamentos_api = DepartamentoSoftdeskService.listar(cliente_id)

        if not departamentos_api:
            self.stdout.write(
                self.style.WARNING(
                    f"Nenhum departamento retornado pela API para o cliente {cliente_id}."
                )
            )
            return

        criados = 0
        atualizados = 0

        for item in departamentos_api:
            codigo = item.get("codigo")
            nome = item.get("descricao") or ""
            status = item.get("status")

            if codigo is None:
                # Sem código de integração não faz sentido sincronizar
                continue

            ativo = True if status in (1, "1", True, "ativo", "Ativo") else False

            obj, created = Departamento.objects.update_or_create(
                codigo_integracao=codigo,
                defaults={
                    "nome": nome,
                    "descricao": nome,
                    "ativo": ativo,
                },
            )

            if created:
                criados += 1
            else:
                atualizados += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Sincronização concluída para o cliente {cliente_id}: "
                f"{criados} criados, {atualizados} atualizados."
            )
        )

