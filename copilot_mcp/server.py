from __future__ import annotations

from mcp.server.fastmcp import FastMCP
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.db import transaction

from contratos.models import (
    Contrato, ContratoArquivo, ContratoClausula, ContratoTarefa, CopilotRun
)
from .permissions import assert_contrato_scope, assert_perm
from .audit import start_run, log_action, finish_run_ok, finish_run_error

mcp = FastMCP("historico-clientes-contratos")


def _get_contrato_checked(user, cliente_id: int, contrato_id: int) -> Contrato:
    contrato = Contrato.objects.select_related("cliente").get(id=contrato_id)
    assert_contrato_scope(user, contrato, cliente_id)
    return contrato


# ------------------------------------------------------------
# TOOL 1: Criar contrato
# ------------------------------------------------------------
@mcp.tool()
def contratos_criar(
    user_id: int,
    cliente_id: int,
    titulo: str,
    descricao: str = "",
    data_inicio_iso: str | None = None,   # "2026-02-23"
    data_fim_iso: str | None = None,
    horas_previstas_total: float = 0.0,
) -> dict:
    """
    Cria um contrato para um cliente.
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.get(id=user_id)

    # perm
    assert_perm(user, "contratos.add_contrato")

    # run (auditoria)
    dummy_contrato = Contrato(cliente_id=cliente_id, titulo=titulo, data_inicio=timezone.now().date())
    # OBS: aqui não temos contrato_id ainda, então run ligado ao contrato não existe.
    # Se você quiser logar mesmo assim, crie outro model "CopilotRunCliente" ou crie o contrato antes e depois cria o run.
    # Vou criar o contrato primeiro e então criar o run (mais simples e consistente).

    try:
        data_inicio = timezone.datetime.fromisoformat(data_inicio_iso).date() if data_inicio_iso else timezone.now().date()
        data_fim = timezone.datetime.fromisoformat(data_fim_iso).date() if data_fim_iso else None

        contrato = Contrato.objects.create(
            cliente_id=cliente_id,
            titulo=titulo,
            descricao=descricao or None,
            data_inicio=data_inicio,
            data_fim=data_fim,
            horas_previstas_total=horas_previstas_total,
        )

        run = start_run(
            contrato=contrato,
            user=user,
            user_message=f"[MCP] contratos.criar: {titulo}",
            mode=CopilotRun.Mode.ACTION,
        )

        log_action(
            run=run,
            action_name="contratos.criar",
            action_input={
                "cliente_id": cliente_id,
                "titulo": titulo,
                "data_inicio": data_inicio_iso,
                "data_fim": data_fim_iso,
                "horas_previstas_total": horas_previstas_total,
            },
            ok=True,
            action_output={"contrato_id": contrato.id},
        )

        finish_run_ok(run, answer=f"Contrato #{contrato.id} criado.")

        return {
            "ok": True,
            "message": f"Contrato #{contrato.id} criado.",
            "data": {"contrato_id": contrato.id, "cliente_id": cliente_id},
            "ui_hint": {"navigate_to": f"/contratos/{contrato.id}"},
        }
    except Exception as e:
        # se não houve run, apenas retorne erro
        return {"ok": False, "message": "Falha ao criar contrato.", "data": {"detail": str(e)}}


# ------------------------------------------------------------
# TOOL 2: Anexar arquivo ao contrato (ContratoArquivo)
#   - aqui eu uso "arquivo_id" como referência a um upload já feito,
#     MAS como você usa FileField, o caminho mais sólido é:
#     (a) upload via endpoint DRF -> cria ContratoArquivo
#     (b) MCP só chama "contratos.processar_arquivo" / "extrair_clausulas"
#
# Para manter MCP autônomo, eu deixo esta tool como "registrar metadados" e assumir que o upload foi feito fora.
# ------------------------------------------------------------
@mcp.tool()
def contratos_registrar_arquivo(
    user_id: int,
    cliente_id: int,
    contrato_id: int,
    tipo: str,                  # use os values do TextChoices
    versao: int = 1,
    nome_original: str | None = None,
    sha256: str | None = None,
) -> dict:
    """
    Registra um arquivo já enviado (upload feito por outro endpoint). Essa tool cria o registro e permite plugar o arquivo depois.
    Se você quiser que o MCP faça upload, precisa suporte a binário/stream no host — geralmente não vale a pena.
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.get(id=user_id)

    contrato = _get_contrato_checked(user, cliente_id, contrato_id)
    assert_perm(user, "contratos.add_contratoarquivo")

    run = start_run(
        contrato=contrato,
        user=user,
        user_message=f"[MCP] contratos.registrar_arquivo: {tipo} v{versao}",
        mode=CopilotRun.Mode.ACTION,
    )

    try:
        ca = ContratoArquivo.objects.create(
            contrato=contrato,
            tipo=tipo,
            versao=versao,
            nome_original=nome_original,
            sha256=sha256,
            extraido_por=None,
        )

        log_action(
            run=run,
            action_name="contratos.registrar_arquivo",
            action_input={"contrato_id": contrato_id, "tipo": tipo, "versao": versao, "nome_original": nome_original, "sha256": sha256},
            action_output={"contrato_arquivo_id": ca.id},
            ok=True,
        )
        finish_run_ok(run, answer=f"Arquivo registrado #{ca.id} no contrato #{contrato_id}.")

        return {
            "ok": True,
            "message": f"Arquivo registrado (id #{ca.id}) no contrato #{contrato_id}.",
            "data": {"contrato_arquivo_id": ca.id, "contrato_id": contrato_id},
            "ui_hint": {"refresh": ["contrato_arquivos"]},
        }
    except Exception as e:
        log_action(run=run, action_name="contratos.registrar_arquivo", action_input={"contrato_id": contrato_id}, ok=False, error=str(e))
        finish_run_error(run, error=str(e))
        return {"ok": False, "message": "Falha ao registrar arquivo.", "data": {"detail": str(e)}}


# ------------------------------------------------------------
# TOOL 3: Extrair cláusulas de um arquivo
#   - marca extraido_em / extraido_por
#   - cria clausulas vinculadas ao contrato e fonte_arquivo
#   - aqui eu deixo um stub de extração: você pluga seu pipeline real (pdf->texto->LLM->cláusulas)
# ------------------------------------------------------------
@mcp.tool()
def contratos_extrair_clausulas(
    user_id: int,
    cliente_id: int,
    contrato_id: int,
    contrato_arquivo_id: int,
    sobrescrever: bool = False,
) -> dict:
    """
    Extrai cláusulas a partir de um ContratoArquivo (PDF).
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.get(id=user_id)

    contrato = _get_contrato_checked(user, cliente_id, contrato_id)
    assert_perm(user, "contratos.add_contratoclausula")

    run = start_run(
        contrato=contrato,
        user=user,
        user_message=f"[MCP] contratos.extrair_clausulas: arquivo #{contrato_arquivo_id}",
        mode=CopilotRun.Mode.EXTRACT_TASKS,
    )

    try:
        ca = ContratoArquivo.objects.select_related("contrato").get(id=contrato_arquivo_id)
        if ca.contrato_id != contrato_id:
            raise PermissionDenied("Arquivo não pertence ao contrato.")

        # Idempotência simples: se já extraído e não sobrescrever
        if ca.extraido_em and not sobrescrever:
            finish_run_ok(run, answer="Arquivo já foi extraído anteriormente.")
            return {
                "ok": True,
                "message": "Esse arquivo já foi extraído. Se quiser reprocessar, use sobrescrever=true.",
                "data": {"contrato_arquivo_id": ca.id, "extraido_em": ca.extraido_em.isoformat()},
            }

        with transaction.atomic():
            # se sobrescrever: apaga cláusulas do arquivo
            if sobrescrever:
                ContratoClausula.objects.filter(fonte_arquivo=ca).delete()

            # --- AQUI ENTRA SEU PIPELINE REAL ---
            # Exemplo mínimo (placeholder): criar 1 cláusula fake
            # Troque por: texto = extrair_texto_pdf(ca.arquivo.path) -> llm_parse(texto) -> lista clausulas
            clausulas = [
                {"numero": "1", "titulo": "Objeto", "texto": "Cláusula exemplo extraída do PDF.", "ordem": 1, "confidence": 90.0},
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
            action_input={"contrato_id": contrato_id, "contrato_arquivo_id": contrato_arquivo_id, "sobrescrever": sobrescrever},
            action_output={"created_clausulas": len(created_ids), "clausula_ids": created_ids[:20]},
            ok=True,
        )
        finish_run_ok(run, answer=f"Extração concluída: {len(created_ids)} cláusulas.")

        return {
            "ok": True,
            "message": f"Extração concluída: {len(created_ids)} cláusulas criadas.",
            "data": {"contrato_arquivo_id": contrato_arquivo_id, "created": len(created_ids)},
            "ui_hint": {"refresh": ["clausulas"]},
        }

    except Exception as e:
        log_action(
            run=run,
            action_name="contratos.extrair_clausulas",
            action_input={"contrato_id": contrato_id, "contrato_arquivo_id": contrato_arquivo_id, "sobrescrever": sobrescrever},
            ok=False,
            error=str(e),
        )
        finish_run_error(run, error=str(e))
        return {"ok": False, "message": "Falha na extração.", "data": {"detail": str(e)}}


# ------------------------------------------------------------
# TOOL 4: Gerar tarefas a partir das cláusulas
#   - usa ContratoTarefa, vincula à clausula
#   - idempotência: não duplicar por (contrato, clausula, titulo)
# ------------------------------------------------------------
@mcp.tool()
def contratos_gerar_tarefas(
    user_id: int,
    cliente_id: int,
    contrato_id: int,
    apenas_sem_tarefas: bool = True,
) -> dict:
    """
    Gera tarefas sugeridas a partir das cláusulas do contrato.
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.get(id=user_id)

    contrato = _get_contrato_checked(user, cliente_id, contrato_id)
    assert_perm(user, "contratos.add_contratotarefa")

    run = start_run(
        contrato=contrato,
        user=user,
        user_message=f"[MCP] contratos.gerar_tarefas",
        mode=CopilotRun.Mode.EXTRACT_TASKS,
    )

    try:
        qs = ContratoClausula.objects.filter(contrato=contrato).order_by("ordem", "id")

        created = 0
        skipped = 0
        created_ids = []

        with transaction.atomic():
            for clausula in qs:
                if apenas_sem_tarefas and clausula.tarefas.exists():
                    skipped += 1
                    continue

                titulo = f"Revisar cumprimento da cláusula {clausula.numero or clausula.id}"
                exists = ContratoTarefa.objects.filter(
                    contrato=contrato,
                    clausula=clausula,
                    titulo=titulo,
                ).exists()
                if exists:
                    skipped += 1
                    continue

                t = ContratoTarefa.objects.create(
                    contrato=contrato,
                    clausula=clausula,
                    titulo=titulo,
                    descricao=(clausula.titulo or "")[:500] or None,
                    responsavel_sugerido="Gerente de Projeto",
                    prioridade="MEDIA",
                    prazo_dias_sugerido=15,
                    gerada_por_ia=True,
                    raw={"source": "mcp", "clausula_id": clausula.id},
                )
                created += 1
                created_ids.append(t.id)

        log_action(
            run=run,
            action_name="contratos.gerar_tarefas",
            action_input={"contrato_id": contrato_id, "apenas_sem_tarefas": apenas_sem_tarefas},
            action_output={"created": created, "skipped": skipped, "tarefa_ids": created_ids[:20]},
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
        log_action(
            run=run,
            action_name="contratos.gerar_tarefas",
            action_input={"contrato_id": contrato_id, "apenas_sem_tarefas": apenas_sem_tarefas},
            ok=False,
            error=str(e),
        )
        finish_run_error(run, error=str(e))
        return {"ok": False, "message": "Falha ao gerar tarefas.", "data": {"detail": str(e)}}