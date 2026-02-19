from __future__ import annotations

from typing import Any, Dict, List

from django.contrib.postgres.search import (
    SearchQuery, SearchRank, SearchHeadline
)
from django.contrib.postgres.search import SearchVector
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import F, Value
from django.db.models.functions import Coalesce

from contratos.models import ContratoClausula
from .rrf import rrf_fuse
from .legal_heuristics import detect_topics, LEGAL_TOPICS


def _build_searchquery(user_query: str, expansion: Dict[str, Any]) -> SearchQuery:
    terms: List[str] = []
    q = (user_query or "").strip()
    if q:
        terms.append(q)
    terms += (expansion.get("keywords") or [])
    terms += (expansion.get("phrases") or [])

    sq = None
    for t in terms:
        part = SearchQuery(t, config="portuguese", search_type="plain")
        sq = part if sq is None else (sq | part)

    return sq or SearchQuery(user_query, config="portuguese", search_type="plain")


def _topic_boost(user_query: str) -> float:
    """
    Boost leve baseado na intenção do usuário.
    Não “adivinha” conteúdo; só aumenta chance de cláusulas temáticas subirem.
    """
    topics = detect_topics(user_query)
    # quanto mais tópicos, mais genérica tende a ser a pergunta; boost menor
    if not topics:
        return 0.0
    if len(topics) == 1:
        return 0.15
    return 0.08


def buscar_clausulas_robusto(
    *,
    contrato_id: int,
    user_query: str,
    expansion: Dict[str, Any],
    limit: int = 8,
) -> List[Dict[str, Any]]:
    """
    1) Gera ranking por FTS
    2) Gera ranking por trigram
    3) Faz fusão (RRF)
    4) Recarrega os objetos + highlight
    """

    sq = _build_searchquery(user_query, expansion)

    # --- Ranking 1: FTS (usa seu search_vector triggerado)
    fts_qs = (
        ContratoClausula.objects
        .filter(contrato_id=contrato_id)
        .annotate(rank=SearchRank("search_vector", sq))
        .order_by("-rank", "ordem")
        .values_list("id", flat=True)[: max(limit * 3, 24)]
    )
    fts_ids = list(fts_qs)

    # --- Ranking 2: Trigram (tolerante a variações)
    # similaridade em titulo + texto
    trigram_qs = (
        ContratoClausula.objects
        .filter(contrato_id=contrato_id)
        .annotate(
            titulo_norm=Coalesce("titulo", Value("")),
            trigram=(
                TrigramSimilarity("texto", user_query) * Value(0.75)
                + TrigramSimilarity("titulo_norm", user_query) * Value(1.25)
            )
        )
        .order_by("-trigram", "ordem")
        .values_list("id", flat=True)[: max(limit * 3, 24)]
    )
    trigram_ids = list(trigram_qs)

    # --- Fusão (robustez)
    fused_ids = rrf_fuse([fts_ids, trigram_ids], limit=limit)

    # Se mesmo assim vier vazio, devolve as primeiras por ordem (fallback duro)
    if not fused_ids:
        fused_ids = list(
            ContratoClausula.objects
            .filter(contrato_id=contrato_id)
            .order_by("ordem")
            .values_list("id", flat=True)[:limit]
        )

    # --- Recarrega com dados + highlight
    # Boost leve por “intenção” (só pra ordenar empates)
    boost = _topic_boost(user_query)

    final_qs = (
        ContratoClausula.objects
        .filter(id__in=fused_ids)
        .annotate(
            rank=SearchRank("search_vector", sq),
            highlight=SearchHeadline(
                "texto",
                sq,
                config="portuguese",
                start_sel="<<",
                stop_sel=">>",
                max_fragments=3,
                min_words=6,
                max_words=32,
            ),
        )
    )

    # preserva ordem da fusão + desempate por rank
    order_map = {doc_id: i for i, doc_id in enumerate(fused_ids)}
    rows = []
    for c in final_qs:
        rows.append({
            "id": c.id,
            "numero": c.numero,
            "titulo": c.titulo,
            "texto": c.texto,
            "ordem": c.ordem,
            "rank": float(getattr(c, "rank", 0) or 0),
            "highlight": getattr(c, "highlight", None),
            "rrf_order": order_map.get(c.id, 9999),
            "boost": boost,
        })

    rows.sort(key=lambda r: (r["rrf_order"], -r["rank"]))
    return rows[:limit]
