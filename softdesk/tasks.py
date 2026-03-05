import logging
from celery import shared_task
from django.core.management import call_command
from django.utils.dateparse import parse_datetime
from django.db import transaction

from helpdesk.models import (
    Chamado, Atendente, UsuarioHelpdesk, ClienteHelpdesk, Area, Impacto, Servico,
    Categoria, ContratoHelpdesk, AtividadeChamado, AnexoChamado,
    FormularioAprovacao, Ligacao, PesquisaSatisfacao, ContestacaoChamado,
    FechamentoAvaliacao
)
from softdesk.services.client import SoftdeskClient

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def sync_softdesk_metadata_task(self):
    """
    Sincroniza tabelas mestre menores. Roda fora do horário de pico.
    """
    logger.info("Iniciando sync_softdesk_metadata_task...")
    call_command("sync_softdesk_metadata")
    logger.info("sync_softdesk_metadata_task concluído.")


@shared_task(bind=True, max_retries=3)
def sync_softdesk_chamados_task(self):
    """
    Busca chamados gerais (histórico) e enfileira busca de detalhes (atividades, anexos).
    """
    client = SoftdeskClient()
    logger.info("Buscando chamados do Softdesk (Header Rate-Limit apply)...")

    # Idealmente, o cliente deve suportar paginação dependendo de como a API Softdesk
    # lida com o GET /chamado, mas se ela retornar tudo, nosso time.sleep()
    # lidará as repetições pesadas de detalhes abaixo.
    try:
        chamados_api = client.get("chamado")
        if not isinstance(chamados_api, list):
            chamados_api = [chamados_api] if chamados_api else []

        logger.info(f"Recebidos {len(chamados_api)} chamados. Processando e enfileirando detalhes...")

        for ch_data in chamados_api:
            # Salvar/Atualizar o chamado básico
            if not isinstance(ch_data, dict):
                continue

            codigo = ch_data.get("codigo")
            if not codigo:
                continue

            # Para simplificar, salvaremos os detalhes depois, mas chamamos outra subtask
            sync_chamado_details_task.delay(codigo)

    except Exception as exc:
        logger.error(f"Erro ao buscar chamados globais: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=5)
def sync_chamado_details_task(self, chamado_codigo):
    """
    Busca todas as tabelas pesadas de um chamado específico:
    Atividades, Anexos, Ligações, Formulario, PesquisaSatisfacao, Fechamento
    """
    client = SoftdeskClient()

    try:
        # Pega o chamado base (criado ou atualizado pelo webhook ou outra task)
        # Se não existe, podemos tentar chamar o endpoint /chamado?codigo=XY e criá-lo.
        chamado_obj = Chamado.objects.filter(codigo_integracao=chamado_codigo).first()

        if not chamado_obj:
            # Tenta buscar do softdesk para criar
            data = client.get("chamado", params={"codigo": chamado_codigo})
            if data and isinstance(data, list):
                ch_data = data[0]
            elif data and isinstance(data, dict):
                ch_data = data
            else:
                logger.warning(f"Chamado {chamado_codigo} não encontrado no Softdesk para detalhes.")
                return

            # Aqui você aplicaria a lógica de Mapeamento/Criação já existente 
            # no Softdesk import_service (simplificado para o exemplo)
            cliente_hd = ClienteHelpdesk.objects.filter(
                codigo_integracao=ch_data.get('cliente', {}).get('codigo')
            ).first() if isinstance(ch_data.get('cliente'), dict) else None

            chamado_obj, _ = Chamado.objects.update_or_create(
                codigo_integracao=chamado_codigo,
                defaults={
                    "titulo": (ch_data.get("titulo") or "Importado")[:255],
                    "descricao": ch_data.get("descricao") or "Sem descrição",
                    "cliente_helpdesk": cliente_hd,
                }
            )

        # 1. Atividades
        atvs = client.get("atividade-chamado", params={"chamado": chamado_codigo})
        atvs = atvs if isinstance(atvs, list) else ([atvs] if atvs else [])
        for a in atvs:
            if not isinstance(a, dict) or not a.get("codigo"): continue
            AtividadeChamado.objects.update_or_create(
                codigo_integracao=a.get("codigo"),
                defaults={
                    "chamado": chamado_obj,
                    "descricao": a.get("descricao", "Atividade Importada"),
                    # Add remaining mappings manually based on actual dict keys returned...
                }
            )

        # 2. Anexos
        anexos = client.get("anexo-chamado", params={"chamado": chamado_codigo})
        anexos = anexos if isinstance(anexos, list) else ([anexos] if anexos else [])
        for anx in anexos:
            if not isinstance(anx, dict) or not anx.get("codigo"): continue
            AnexoChamado.objects.update_or_create(
                codigo_integracao=anx.get("codigo"),
                defaults={
                    "chamado": chamado_obj,
                    "nome_original": anx.get("nome_arquivo") or "anexo",
                    # Handle file download if necessary, careful with large files and limits!
                }
            )

        # 3. Formulario, Fechamento, Ligação, Satisfação seguiriam a mesma lógica.
        # Exemplo Ligaçao
        ligs = client.get("ligacao", params={"chamado": chamado_codigo})
        ligs = ligs if isinstance(ligs, list) else ([ligs] if ligs else [])
        for lig in ligs:
            if not isinstance(lig, dict) or not lig.get("codigo"): continue
            Ligacao.objects.update_or_create(
                codigo_integracao=lig.get("codigo"),
                defaults={
                    "chamado": chamado_obj,
                    "telefone_origem": str(lig.get("telefone_origem", ""))[:30],
                }
            )

    except Exception as exc:
        logger.error(f"Erro na sync de detalhes do chamado {chamado_codigo}: {exc}")
        # SoftdeskClient levantará Exception com 429 se estourou muito
        # O self.retry joga de volta na fila
        raise self.retry(exc=exc, countdown=120)
