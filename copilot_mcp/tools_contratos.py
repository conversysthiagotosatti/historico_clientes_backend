from __future__ import annotations

from django.db import transaction
from django.utils import timezone
from django.core.exceptions import PermissionDenied

from contratos.models import (
    Contrato, ContratoArquivo, ContratoClausula, ContratoTarefa, CopilotRun
)
from .audit import start_run, log_action, finish_run_ok, finish_run_error
from .permissions import assert_perm, assert_contrato_scope


# -----------------------------
# DISCOVERY TOOLS
# -----------------------------
def _iso(v):
    try:
        return v.isoformat() if v is not None else None
    except Exception:
        return v

def contratos_listar(*, user, cliente_id: int, limit: int = 10):
    assert_perm(user, "contratos.view_contrato")
    items = list(
        Contrato.objects.filter(cliente_id=cliente_id)
        .order_by("-id")
        .values("id", "cliente_id", "titulo", "data_inicio", "data_fim")[:limit]
    )

    for it in items:
        it["data_inicio"] = _iso(it.get("data_inicio"))
        it["data_fim"] = _iso(it.get("data_fim"))

    return {"ok": True, "message": "Contratos listados.", "data": {"items": items}}


def contratos_get(*, user, cliente_id: int, contrato_id: int):
    assert_perm(user, "contratos.view_contrato")
    c = Contrato.objects.filter(id=contrato_id).values(
        "id", "cliente_id", "titulo", "descricao", "data_inicio", "data_fim", "horas_previstas_total"
    ).first()

    if not c:
        return {"ok": False, "message": f"Contrato {contrato_id} não encontrado.", "error_code": "CONTRATO_NOT_FOUND"}
    if c["cliente_id"] != cliente_id:
        return {"ok": False, "message": "Contrato não pertence ao cliente informado.", "error_code": "SCOPE_MISMATCH"}

    c["data_inicio"] = _iso(c.get("data_inicio"))
    c["data_fim"] = _iso(c.get("data_fim"))
    # Decimal pode virar string também (opcional). DjangoJSONEncoder já resolve.

    return {"ok": True, "message": "Contrato encontrado.", "data": c}


def contratos_arquivos_listar(*, user, cliente_id: int, contrato_id: int, limit: int = 20):
    assert_perm(user, "contratos.view_contratoarquivo")

    contrato = Contrato.objects.select_related("cliente").filter(id=contrato_id).first()
    if not contrato:
        return {"ok": False, "message": f"Contrato {contrato_id} não encontrado.", "error_code": "CONTRATO_NOT_FOUND"}
    assert_contrato_scope(user, contrato, cliente_id)

    qs = (
        ContratoArquivo.objects.filter(contrato_id=contrato_id)
        .order_by("-criado_em")
        .values("id", "contrato_id", "tipo", "versao", "nome_original", "sha256", "extraido_em")[:limit]
    )
    return {"ok": True, "message": "Arquivos do contrato listados.", "data": {"items": list(qs)}}


# -----------------------------
# ACTION TOOLS
# -----------------------------
def contratos_extrair_clausulas(
    *, user, cliente_id: int, contrato_id: int, contrato_arquivo_id: int, sobrescrever: bool = False
):
    assert_perm(user, "contratos.add_contratoclausula")

    contrato = Contrato.objects.select_related("cliente").filter(id=contrato_id).first()
    if not contrato:
        return {"ok": False, "message": f"Contrato {contrato_id} não encontrado.", "error_code": "CONTRATO_NOT_FOUND"}
    assert_contrato_scope(user, contrato, cliente_id)

    run = start_run(
        contrato=contrato,
        user=user,
        user_message=f"Extrair cláusulas do arquivo {contrato_arquivo_id}",
        mode=CopilotRun.Mode.EXTRACT_TASKS,
        model="copilot-tools",
        prompt_version="tools-contratos-v1",
    )

    try:
        ca = ContratoArquivo.objects.select_related("contrato").filter(id=contrato_arquivo_id).first()
        if not ca:
            return {"ok": False, "message": f"Arquivo {contrato_arquivo_id} não encontrado.", "error_code": "ARQUIVO_NOT_FOUND"}
        if ca.contrato_id != contrato_id:
            raise PermissionDenied("Arquivo não pertence ao contrato.")

        if ca.extraido_em and not sobrescrever:
            log_action(
                run=run,
                action_name="contratos.extrair_clausulas",
                action_input={"cliente_id": cliente_id, "contrato_id": contrato_id, "contrato_arquivo_id": contrato_arquivo_id, "sobrescrever": sobrescrever},
                action_output={"skipped": True, "extraido_em": ca.extraido_em.isoformat()},
                ok=True,
            )
            finish_run_ok(run, answer="Arquivo já extraído.")
            return {
                "ok": True,
                "message": "Esse arquivo já foi extraído. Use sobrescrever=true para reprocessar.",
                "data": {"extraido_em": ca.extraido_em.isoformat()},
            }

        with transaction.atomic():
            if sobrescrever:
                ContratoClausula.objects.filter(fonte_arquivo=ca).delete()

            # TODO: PLUGUE SEU PIPELINE REAL AQUI (PDF -> texto -> LLM -> cláusulas)
            clausulas = [
                {"numero": "1", "titulo": "Objeto", "texto": "Cláusula exemplo extraída do PDF.", "ordem": 1, "confidence": 90.0},
                {"numero": "2", "titulo": "Vigência", "texto": "Cláusula exemplo de vigência.", "ordem": 2, "confidence": 88.0},
            ]

            created_ids = []
            for c in clausulas:
                obj = ContratoClausula.objects.create(
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
                created_ids.append(obj.id)

            ca.extraido_em = timezone.now()
            ca.extraido_por = user
            ca.save(update_fields=["extraido_em", "extraido_por"])

        log_action(
            run=run,
            action_name="contratos.extrair_clausulas",
            action_input={"cliente_id": cliente_id, "contrato_id": contrato_id, "contrato_arquivo_id": contrato_arquivo_id, "sobrescrever": sobrescrever},
            action_output={"created": len(created_ids), "clausula_ids": created_ids[:20]},
            ok=True,
        )
        finish_run_ok(run, answer=f"Extração concluída: {len(created_ids)} cláusulas.")

        return {
            "ok": True,
            "message": f"Extração concluída: {len(created_ids)} cláusulas criadas.",
            "data": {"created": len(created_ids)},
            "ui_hint": {"refresh": ["clausulas"]},
        }

    except Exception as e:
        log_action(
            run=run,
            action_name="contratos.extrair_clausulas",
            action_input={"cliente_id": cliente_id, "contrato_id": contrato_id, "contrato_arquivo_id": contrato_arquivo_id, "sobrescrever": sobrescrever},
            ok=False,
            error=str(e),
        )
        finish_run_error(run, error=str(e))
        return {"ok": False, "message": "Falha na extração.", "data": {"detail": str(e)}}


def contratos_gerar_tarefas(*, user, cliente_id: int, contrato_id: int, apenas_sem_tarefas: bool = True):
    assert_perm(user, "contratos.add_contratotarefa")

    contrato = Contrato.objects.select_related("cliente").filter(id=contrato_id).first()
    if not contrato:
        return {"ok": False, "message": f"Contrato {contrato_id} não encontrado.", "error_code": "CONTRATO_NOT_FOUND"}
    assert_contrato_scope(user, contrato, cliente_id)

    run = start_run(
        contrato=contrato,
        user=user,
        user_message="Gerar tarefas a partir das cláusulas",
        mode=CopilotRun.Mode.EXTRACT_TASKS,
        model="copilot-tools",
        prompt_version="tools-contratos-v1",
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
                    raw={"source": "copilot-tools", "clausula_id": clausula.id},
                )
                created += 1

        log_action(
            run=run,
            action_name="contratos.gerar_tarefas",
            action_input={"cliente_id": cliente_id, "contrato_id": contrato_id, "apenas_sem_tarefas": apenas_sem_tarefas},
            action_output={"created": created, "skipped": skipped},
            ok=True,
        )
        finish_run_ok(run, answer=f"Tarefas geradas: {created} (skipped: {skipped}).")

        return {
            "ok": True,
            "message": f"Tarefas geradas: {created} (ignoradas: {skipped}).",
            "data": {"created": created, "skipped": skipped},
            "ui_hint": {"navigate_to": f"/contratos/{contrato_id}/tarefas"},
        }

    except Exception as e:
        log_action(run=run, action_name="contratos.gerar_tarefas", action_input={"cliente_id": cliente_id, "contrato_id": contrato_id}, ok=False, error=str(e))
        finish_run_error(run, error=str(e))
        return {"ok": False, "message": "Falha ao gerar tarefas.", "data": {"detail": str(e)}}