# contratos/copilot/service.py
from openai import OpenAI
from contratos.copilot.expand_query import expand_semantic_query
from contratos.models import Contrato
from contratos.copilot.retriever_fts import buscar_clausulas_relevantes

SYSTEM_PROMPT = """Você é um Co-Pilot do módulo de Contratos.
Regras:
- Use SOMENTE as cláusulas fornecidas como contexto.
- Se não houver evidência suficiente, diga claramente.
- Cite as cláusulas usadas (ids) na resposta.
- Não invente termos/obrigações.
"""

def responder_pergunta_contrato(*, user, contrato_id: int, pergunta: str):
    contrato = Contrato.objects.select_related("cliente").get(id=contrato_id)

    # (muito importante) isolar por cliente (multi-tenant)
    # ajuste conforme seu RBAC real:
    # se você tiver user.cliente_id:
    # if contrato.cliente_id != user.cliente_id: raise PermissionDenied()
    expansion = expand_semantic_query(pergunta)
    
    clausulas = buscar_clausulas_relevantes(
        contrato_id=contrato_id,
        user_query=pergunta,
        expansion=expansion,
        limit=1000,
    )

    contexto = "\n\n".join(
        [
            f"[CLAUSULA_ID={c['id']}] Numero: {c.get('numero')} | Titulo: {c.get('titulo')}\nTexto: {c['texto']}"
            for c in clausulas
        ]
    ) or "NENHUMA CLAUSULA RELEVANTE ENCONTRADA."

    prompt = f"""
Contrato: {contrato.titulo}
Pergunta do usuário: {pergunta}

Contexto (cláusulas):
{contexto}

Responda de forma objetiva e cite quais CLAUSULA_IDs usou.
"""

    client = OpenAI()  # precisa OPENAI_API_KEY no ambiente
    resp = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {"role": "system", "content": [{"type": "input_text", "text": SYSTEM_PROMPT}]},
            {"role": "user", "content": [{"type": "input_text", "text": prompt}]},
        ],
    )

    return {
        "contrato_id": contrato_id,
        "answer": resp.output_text,
        "clausulas_usadas": [{"id": c["id"], "rank": float(c["rank"]), "highlight": c.get("highlight")} for c in clausulas],
    }
