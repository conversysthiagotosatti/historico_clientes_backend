def rrf_fuse(rankings: list[list[int]], k: int = 60, limit: int = 8) -> list[int]:
    """
    Reciprocal Rank Fusion.
    rankings: listas de IDs ordenadas por relevância, cada lista vindo de um método.
    """
    scores = {}
    for lst in rankings:
        for i, doc_id in enumerate(lst):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + i + 1)
    return [doc_id for doc_id, _ in sorted(scores.items(), key=lambda x: x[1], reverse=True)[:limit]]
