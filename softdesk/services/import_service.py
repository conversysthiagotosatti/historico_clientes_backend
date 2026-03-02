from django.db import transaction
from datetime import datetime
from django.utils import timezone

from softdesk.models import SoftdeskChamado
from .chamados_service import ChamadoService


class ImportSoftdeskService:

    @staticmethod
    @transaction.atomic
    def importar_chamado(cliente_id: int, codigo: int) -> SoftdeskChamado:

        data = ChamadoService.buscar_por_codigo(cliente_id, codigo)

        if not data:
            raise Exception("Chamado não encontrado na API")

        chamado = data[0] if isinstance(data, list) else data

        data_abertura = ImportSoftdeskService._parse_datetime(
            chamado.get("data_abertura")
        )

        data_fechamento = ImportSoftdeskService._parse_datetime(
            chamado.get("data_fechamento")
        )

        obj, _ = SoftdeskChamado.objects.update_or_create(
            codigo=codigo,
            defaults={
                "cliente_id": cliente_id,
                "titulo": chamado.get("titulo") or chamado.get("assunto"),
                "status": chamado.get("status"),
                "cliente_codigo": chamado.get("cliente_codigo"),
                "data_abertura": data_abertura,
                "data_fechamento": data_fechamento,
                "raw": chamado,
            }
        )

        return obj

    @staticmethod
    def _parse_datetime(valor):
        if not valor:
            return None

        try:
            return datetime.strptime(
                valor,
                "%Y-%m-%d %H:%M:%S"
            ).replace(tzinfo=timezone.utc)
        except Exception:
            return None