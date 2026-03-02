from django.core.management.base import BaseCommand
from softdesk.services.import_service import ImportSoftdeskService


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("codigo", type=int)

    def handle(self, *args, **kwargs):
        codigo = kwargs["codigo"]

        chamado = ImportSoftdeskService.importar_chamado(codigo)

        self.stdout.write(
            self.style.SUCCESS(f"Chamado {chamado.codigo} importado com sucesso.")
        )