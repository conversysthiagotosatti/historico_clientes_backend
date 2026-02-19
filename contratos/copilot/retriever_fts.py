# contratos/copilot/retriever_fts.py
from __future__ import annotations

from typing import Dict, Any, List

from django.contrib.postgres.search import SearchQuery, SearchRank, SearchHeadline
from django.db.models import Q

from contratos.models import ContratoClausula


def build_expanded_searchquery(user_query: str, expansion: Dict[str, Any]) -> SearchQuery:
    """
    Constrói SearchQuery com OR entre termos (keywords + frases + consulta original).
    """
    terms: List[str] = []

    q = (user_query or "").strip()
    if q:
        terms.append(q)

    terms += (expansion.get("keywords") or [])
    terms += (expansion.get("phrases") or [])

    # Cria OR entre SearchQuery(term)
    sq = None
    for t in terms:
        # plain costuma ser mais previsível que websearch para PT-BR em contratos
        part = SearchQuery(t, config="portuguese", search_type="plain")
        sq = part if sq is None else (sq | part)

    # fallback: se tudo falhar
    if sq is None:
        sq = SearchQuery(user_query, config="portuguese", search_type="plain")
    return sq


def buscar_clausulas_relevantes(
    *,
    contrato_id: int,
    user_query: str,
    expansion: Dict[str, Any],
    limit: int = 8,
):
    q = build_expanded_searchquery(user_query, expansion)

    qs = (
        ContratoClausula.objects
        .filter(contrato_id=contrato_id)
        .annotate(rank=SearchRank("search_vector", q))
        .order_by("-rank", "ordem")
    )

    # ✅ não corte agressivo por rank (evita resposta vazia)
    qs = qs[:limit]

    # highlight do texto
    qs = qs.annotate(
        highlight=SearchHeadline(
            "texto",
            q,
            config="portuguese",
            start_sel="<<",
            stop_sel=">>",
            max_fragments=2,
            min_words=8,
            max_words=30,
        )
    )

    results = list(qs.values("id", "numero", "titulo", "texto", "ordem", "rank", "highlight"))

    # ✅ fallback (se rank vier tudo 0): tenta icontains em cima de alguns termos
    if not results or all((float(r["rank"] or 0) == 0.0) for r in results):
        fallback_terms = [user_query] + (expansion.get("keywords") or [])[:4]
        fallback_q = Q(contrato_id=contrato_id)
        for t in fallback_terms:
            if t:
                fallback_q &= (Q(texto__icontains=t) | Q(titulo__icontains=t))

        fb = list(
            ContratoClausula.objects
            .filter(fallback_q)
            .order_by("ordem")[:limit]
            .values("id", "numero", "titulo", "texto", "ordem")
        )
        # rank inexistente no fallback
        for r in fb:
            r["rank"] = 0.0
            r["highlight"] = None
        return fb

    return results
