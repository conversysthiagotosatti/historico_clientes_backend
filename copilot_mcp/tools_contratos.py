from __future__ import annotations

from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.db import transaction

from contratos.models import Contrato, ContratoArquivo, ContratoClausula, ContratoTarefa, CopilotRun
from .audit import start_run, log_action, finish_run_ok, finish_run_error
from .permissions import assert_perm, assert_contrato_scope


def contratos_criar(*, user, cliente_id: int, titulo: str, data_inicio_iso: str, descricao: str = "", data_fim_iso: str | None = None):
    assert_perm(user, "contratos.add_contrato")

    data_inicio = timezone.datetime.fromisoformat(data_inicio_iso).date()
    data_fim = timezone.datetime.fromisoformat(data_fim_iso).date() if data_fim_iso else None

    contrato = Contrato.objects.create(
        cliente_id=cliente_id,
        titulo=titulo,
        descricao=descricao or None,
        data_inicio=data_inicio,
        data_fim=data_fim,
    )

    run = start_run(
        contrato=contrato,
        user=user,
        user_message=f"Criar contrato: {titulo}",
        mode=CopilotRun.Mode.ACTION,
        model="mcp-runtime",
        prompt_version="mcp-contratos-v1",
    )
    log_action(run=run, action_name="contratos.criar", action_input={"cliente_id": cliente_id, "titulo": titulo}, action_output={"contrato_id": contrato.id}, ok=True)
    finish_run_ok(run, answer=f"Contrato #{contrato.id} criado.")

    return {"ok": True, "message": f"Contrato #{contrato.id} criado.", "data": {"contrato_id": contrato.id}}


def contratos_extrair_clausulas(*, user, cliente_id: int, contrato_id: int, contrato_arquivo_id: int, sobrescrever: bool = False):
    assert_perm(user, "contratos.add_contratoclausula")

    contrato = Contrato.objects.select_related("cliente").get(id=contrato_id)
    assert_contrato_scope(user, contrato, cliente_id)

    run = start_run(
        contrato=contrato,
        user=user,
        user_message=f"Extrair cláusulas do arquivo {contrato_arquivo_id}",
        mode=CopilotRun.Mode.EXTRACT_TASKS,
        model="mcp-runtime",
        prompt_version="mcp-contratos-v1",
    )

    try:
        ca = ContratoArquivo.objects.select_related("contrato").get(id=contrato_arquivo_id)
        if ca.contrato_id != contrato_id:
            raise PermissionDenied("Arquivo não pertence ao contrato.")

        if ca.extraido_em and not sobrescrever:
            finish_run_ok(run, answer="Arquivo já extraído.")
            return {"ok": True, "message": "Arquivo já extraído. Use sobrescrever=true para reprocessar.", "data": {"extraido_em": ca.extraido_em.isoformat()}}

        with transaction.atomic():
            if sobrescrever:
                ContratoClausula.objects.filter(fonte_arquivo=ca).delete()

            # Placeholder: substitua pelo seu pipeline real
            clausulas = [
                {"numero": "1", "titulo": "Objeto", "texto": "Cláusula exemplo extraída do PDF.", "ordem": 1, "confidence": 90.0},
            ]

            created = 0
            for c in clausulas:
                ContratoClausula.objects.create(
                    contrato=contrato,
                    fonte_arquivo=ca,
                    numero=c.get("numero"),
                    titulo=c.get("titulo"),
                    texto=c["texto"],
                    ordem=c.get("ordem", 0),
                    extraida_por_ia=True,
                    confidence=c.get("confidence"),
                    raw=c,
                )
                created += 1

            ca.extraido_em = timezone.now()
            ca.extraido_por = user
            ca.save(update_fields=["extraido_em", "extraido_por"])

        log_action(run=run, action_name="contratos.extrair_clausulas", action_input={"contrato_id": contrato_id, "contrato_arquivo_id": contrato_arquivo_id, "sobrescrever": sobrescrever}, action_output={"created": created}, ok=True)
        finish_run_ok(run, answer=f"Extração concluída: {created} cláusulas.")

        return {"ok": True, "message": f"Extração concluída: {created} cláusulas criadas.", "data": {"created": created}}

    except Exception as e:
        log_action(run=run, action_name="contratos.extrair_clausulas", action_input={"contrato_id": contrato_id, "contrato_arquivo_id": contrato_arquivo_id}, ok=False, error=str(e))
        finish_run_error(run, error=str(e))
        return {"ok": False, "message": "Falha na extração.", "data": {"detail": str(e)}}


def contratos_gerar_tarefas(*, user, cliente_id: int, contrato_id: int, apenas_sem_tarefas: bool = True):
    assert_perm(user, "contratos.add_contratotarefa")

    contrato = Contrato.objects.select_related("cliente").get(id=contrato_id)
    assert_contrato_scope(user, contrato, cliente_id)

    run = start_run(
        contrato=contrato,
        user=user,
        user_message="Gerar tarefas a partir das cláusulas",
        mode=CopilotRun.Mode.EXTRACT_TASKS,
        model="mcp-runtime",
        prompt_version="mcp-contratos-v1",
    )

    try:
        created = 0
        skipped = 0

        with transaction.atomic():
            for clausula in ContratoClausula.objects.filter(contrato=contrato).order_by("ordem", "id"):
                if apenas_sem_tarefas and clausula.tarefas.exists():
                    skipped += 1
                    continue

                titulo = f"Revisar cumprimento da cláusula {clausula.numero or clausula.id}"
                if ContratoTarefa.objects.filter(contrato=contrato, clausula=clausula, titulo=titulo).exists():
                    skipped += 1
                    continue

                ContratoTarefa.objects.create(
                    contrato=contrato,
                    clausula=clausula,
                    titulo=titulo,
                    descricao=(clausula.titulo or "")[:500] or None,
                    responsavel_sugerido="Gerente de Projeto",
                    prioridade="MEDIA",
                    prazo_dias_sugerido=15,
                    gerada_por_ia=True,
                    raw={"source": "mcp-runtime", "clausula_id": clausula.id},
                )
                created += 1

        log_action(run=run, action_name="contratos.gerar_tarefas", action_input={"contrato_id": contrato_id, "apenas_sem_tarefas": apenas_sem_tarefas}, action_output={"created": created, "skipped": skipped}, ok=True)
        finish_run_ok(run, answer=f"Tarefas geradas: {created}.")

        return {"ok": True, "message": f"Tarefas geradas: {created} (ignoradas: {skipped}).", "data": {"created": created, "skipped": skipped}}

    except Exception as e:
        log_action(run=run, action_name="contratos.gerar_tarefas", action_input={"contrato_id": contrato_id}, ok=False, error=str(e))
        finish_run_error(run, error=str(e))
        return {"ok": False, "message": "Falha ao gerar tarefas.", "data": {"detail": str(e)}}