# contratos/copilot/service.py
from __future__ import annotations

import time
from typing import Any

from openai import OpenAI

from contratos.models import Contrato
from contratos.models import CopilotRun  # ajuste import se você colocou no models.py

from .expand_query import expand_semantic_query
from .retriever_legal import buscar_clausulas_robusto
from .policies import assert_contrato_access

MODEL_NAME = "gpt-4o-mini"
PROMPT_VERSION = "contracts-copilot-v1"

SYSTEM_PROMPT = """Você é um Co-Pilot do módulo de Contratos.
Regras:
- Use SOMENTE as cláusulas fornecidas como contexto.
- Se não houver evidência suficiente, diga claramente o que faltou.
- Cite os CLAUSULA_IDs usados (obrigatório).
- Não invente obrigações/prazos.
Formato:
- Responda em tópicos curtos quando possível.
- Ao final, liste "Citações: [ids...]"
"""


def _calc_confidence(clausulas: list[dict]) -> float:
    # Heurística simples e útil:
    # - mais evidência + ranks maiores => mais confiança
    if not clausulas:
        return 0.10
    ranks = [float(c.get("rank") or 0) for c in clausulas]
    top = max(ranks) if ranks else 0.0
    coverage = min(len(clausulas) / 6.0, 1.0)
    # normalização leve
    conf = 0.25 + (0.55 * min(top * 4, 1.0)) + (0.20 * coverage)
    return max(0.0, min(conf, 0.95))


def buscar_clausulas_relevantes(
    *,
    contrato_id: int,
    user_query: str | None = None,
    query_text: str | None = None,
    expansion: dict[str, Any] | None = None,
    limit: int = 8,
) -> list[dict]:
    """
    Wrapper de compatibilidade:
    - aceita `query_text` (legado) e `user_query` (novo)
    - garante retorno como lista
    """
    q = (user_query or query_text or "").strip()
    if not q:
        return []

    exp = expansion if expansion is not None else expand_semantic_query(q)

    items = buscar_clausulas_robusto(
        contrato_id=contrato_id,
        user_query=q,
        expansion=exp,
        limit=limit,
    )
    return items or []


def responder_pergunta_contrato(*, user, contrato_id: int, pergunta: str) -> dict:
    start = time.perf_counter()

    contrato = Contrato.objects.select_related("cliente").get(id=contrato_id)
    assert_contrato_access(user, contrato)

    run = CopilotRun.objects.create(
        contrato=contrato,
        cliente=contrato.cliente,
        usuario=user,
        mode=CopilotRun.Mode.QA,
        status=CopilotRun.Status.OK,
        user_message=pergunta,
        model=MODEL_NAME,
        prompt_version=PROMPT_VERSION,
    )

    try:
        expansion = expand_semantic_query(pergunta)

        # ✅ robusto e compatível (não quebra se alguém mudar o nome do argumento em outro lugar)
        clausulas = buscar_clausulas_relevantes(
            contrato_id=contrato_id,
            user_query=pergunta,
            expansion=expansion,
            limit=8,
        )

        # contexto (✅ evita KeyError se alguma chave vier faltando)
        contexto = "\n\n".join(
            [
                (
                    f"[CLAUSULA_ID={c.get('id')}] "
                    f"Numero: {c.get('numero')} | Titulo: {c.get('titulo')}\n"
                    f"Texto: {c.get('texto', '')}"
                )
                for c in clausulas
            ]
        ) or "NENHUMA CLAUSULA RELEVANTE ENCONTRADA."

        prompt = f"""
Contrato: {contrato.titulo}
Pergunta do usuário: {pergunta}

Termos expandidos:
keywords={expansion.get("keywords")}
phrases={expansion.get("phrases")}

Contexto (cláusulas):
{contexto}

Responda de forma objetiva e cite quais CLAUSULA_IDs usou.
"""

        client = OpenAI()
        resp = client.responses.create(
            model=MODEL_NAME,
            input=[
                {"role": "system", "content": [{"type": "input_text", "text": SYSTEM_PROMPT}]},
                {"role": "user", "content": [{"type": "input_text", "text": prompt}]},
            ],
        )

        answer = resp.output_text

        # explicabilidade: evidências (citations)
        citations = [
            {
                "clausula_id": c.get("id"),
                "numero": c.get("numero"),
                "titulo": c.get("titulo"),
                "rank": float(c.get("rank") or 0),
                "highlight": c.get("highlight"),
            }
            for c in clausulas
        ]

        confidence = _calc_confidence(clausulas)

        latency_ms = int((time.perf_counter() - start) * 1000)

        # token_usage pode variar conforme SDK; guardamos defensivamente
        token_usage = None
        try:
            token_usage = getattr(resp, "usage", None) or getattr(resp, "usage_total", None)
        except Exception:
            token_usage = None

        run.query_expansion = expansion
        run.retrieved = {"items": citations, "retriever": "legal_hybrid_rrf"}
        run.citations = citations
        run.answer = answer
        run.latency_ms = latency_ms
        run.token_usage = token_usage
        run.save(
            update_fields=[
                "query_expansion",
                "retrieved",
                "citations",
                "answer",
                "latency_ms",
                "token_usage",
            ]
        )

        return {
            "run_id": run.id,
            "contrato_id": contrato_id,
            "answer": answer,
            "confidence": confidence,
            "citations": citations,
        }

    except Exception as e:
        latency_ms = int((time.perf_counter() - start) * 1000)
        run.status = CopilotRun.Status.ERROR
        run.error = str(e)
        run.latency_ms = latency_ms
        run.save(update_fields=["status", "error", "latency_ms"])
        raise
