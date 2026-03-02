from django.db import transaction
from django.utils import timezone
from datetime import datetime

from softdesk.models import SoftdeskChamado
from helpdesk.models import Chamado, Setor, ChamadoStatus, ChamadoPrioridade
from django.contrib.auth import get_user_model

from .chamados_service import ChamadoService

User = get_user_model()


class ImportSoftdeskService:

    @staticmethod
    @transaction.atomic
    def importar_chamado(cliente_id: int, codigo: int):

        # 🔹 1️⃣ Buscar na API
        data = ChamadoService.buscar_por_codigo(cliente_id, codigo)

        if not data:
            raise Exception("Chamado não encontrado na API")

        chamado_api = data[0] if isinstance(data, list) else data

        # 🔹 2️⃣ Gravar na tabela SoftdeskChamado (espelho bruto)
        softdesk_obj, _ = SoftdeskChamado.objects.update_or_create(
            cliente_id=cliente_id,
            codigo=codigo,
            defaults={
                "titulo": chamado_api.get("titulo"),
                "status": chamado_api.get("status"),
                "raw": chamado_api,
            }
        )

        # 🔹 3️⃣ Mapear dados para tabela interna Chamado

        titulo = chamado_api.get("titulo") or f"Chamado Softdesk #{codigo}"
        descricao = chamado_api.get("descricao") or chamado_api.get("detalhes") or "Importado do Softdesk"

        # ⚠️ Ajuste conforme sua regra real
        setor = Setor.objects.first()
        solicitante = User.objects.first()

        chamado_interno = Chamado.objects.create(
            titulo=titulo,
            descricao=descricao,
            setor=setor,
            solicitante=solicitante,
            status=ChamadoStatus.ABERTO,
            prioridade=ChamadoPrioridade.MEDIA,
        )

        return {
            "softdesk": softdesk_obj,
            "chamado": chamado_interno
        }