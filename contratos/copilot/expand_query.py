# contratos/copilot/expand_query.py
from __future__ import annotations

import hashlib
import json
import re
from typing import List, Dict, Any

from django.core.cache import cache
from openai import OpenAI


EXPANSION_SCHEMA = {
    "name": "fts_query_expansion",
    "strict": True,
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "keywords": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Palavras-chave unitárias (sem frases longas).",
            },
            "phrases": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Expressões curtas úteis para contratos (2 a 5 palavras).",
            },
            "negative": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Termos a evitar (opcional).",
            },
        },
        "required": ["keywords", "phrases", "negative"],
    },
}

SYSTEM_PROMPT = """Você é um assistente especializado em contratos.
Sua tarefa é EXPANDIR a consulta do usuário para melhorar recuperação via Full-Text Search (PostgreSQL).
Regras:
- Retorne APENAS JSON válido conforme o schema.
- Gere termos em português, focados em linguagem contratual/jurídica.
- Não invente fatos do contrato.
- Preferir sinônimos e termos juridicamente comuns.
- Limites: no máximo 10 keywords e 6 phrases.
- Evite repetir o termo original muitas vezes.
- Se a consulta for genérica (ex: "obrigações", "prazos"), inclua termos clássicos de contratos relacionados.
"""

# Seeds para perguntas genéricas (contratos)
GENERIC_SEEDS: Dict[str, Dict[str, List[str]]] = {
    "obrigacoes": {
        "keywords": ["deveres", "responsabilidades", "encargos", "atribuições", "prestação", "execução", "escopo"],
        "phrases": ["obrigações da contratada", "obrigações do contratado", "responsabilidades das partes"],
    },
    "prazos": {
        "keywords": ["vigência", "vencimento", "renovação", "prazo", "término", "cronograma"],
        "phrases": ["prazo de execução", "data de início e término", "prazo de vigência"],
    },
    "multa": {
        "keywords": ["penalidade", "sanção", "cláusula penal", "indenização", "juros", "mora"],
        "phrases": ["multa por descumprimento", "penalidades contratuais"],
    },
    "rescisao": {
        "keywords": ["rescisão", "resolucao", "distrato", "denúncia", "encerramento"],
        "phrases": ["hipóteses de rescisão", "rescisão unilateral", "prazo de aviso prévio"],
    },
}


def _clean_terms(terms: List[str], max_len: int = 48) -> List[str]:
    cleaned: List[str] = []
    seen = set()

    for t in terms:
        if not isinstance(t, str):
            continue

        t = t.strip()
        t = re.sub(r"\s+", " ", t)
        t = t.strip('"').strip("'").strip()

        if not t:
            continue

        if len(t) > max_len:
            t = t[:max_len].rstrip()

        # remove termos genéricos demais que pouco ajudam no FTS
        if t.lower() in {"contrato", "cláusula", "clausula", "partes"}:
            continue

        key = t.lower()
        if key in seen:
            continue

        seen.add(key)
        cleaned.append(t)

    return cleaned


def _fallback_expansion(user_query: str) -> Dict[str, Any]:
    """
    Fallback determinístico (sem IA): garante expansão mínima sempre.
    """
    q = (user_query or "").lower()
    out_keywords: List[str] = []
    out_phrases: List[str] = []

    if "obriga" in q or "responsab" in q or "dever" in q:
        out_keywords += GENERIC_SEEDS["obrigacoes"]["keywords"]
        out_phrases += GENERIC_SEEDS["obrigacoes"]["phrases"]

    if "prazo" in q or "vig" in q or "venc" in q or "data" in q:
        out_keywords += GENERIC_SEEDS["prazos"]["keywords"]
        out_phrases += GENERIC_SEEDS["prazos"]["phrases"]

    if "multa" in q or "penal" in q or "sanç" in q:
        out_keywords += GENERIC_SEEDS["multa"]["keywords"]
        out_phrases += GENERIC_SEEDS["multa"]["phrases"]

    if "rescis" in q or "encerr" in q or "distr" in q:
        out_keywords += GENERIC_SEEDS["rescisao"]["keywords"]
        out_phrases += GENERIC_SEEDS["rescisao"]["phrases"]

    if not out_keywords and not out_phrases:
        out_keywords = ["escopo", "vigência", "multa", "rescisão", "pagamento", "prazo", "responsabilidades"]
        out_phrases = ["obrigações das partes", "condições de pagamento", "prazo e vigência"]

    return {
        "keywords": _clean_terms(out_keywords, max_len=32)[:10],
        "phrases": _clean_terms(out_phrases, max_len=64)[:6],
        "negative": [],
    }


def expand_semantic_query(user_query: str, *, model: str = "gpt-4o-mini") -> Dict[str, Any]:
    """
    Retorna termos expandidos para usar em FTS.
    - Cache (24h)
    - Fallback determinístico se OpenAI falhar
    - Seeds jurídicos para perguntas genéricas
    """
    q = (user_query or "").strip()
    if not q:
        return {"keywords": [], "phrases": [], "negative": []}

    # ✅ Cache por query normalizada + model
    norm = re.sub(r"\s+", " ", q.lower()).strip()
    cache_key = "copilot:exp:" + hashlib.sha256(f"{model}:{norm}".encode("utf-8")).hexdigest()
    cached = cache.get(cache_key)
    if cached:
        return cached

    # Seeds ajudam a evitar expansão ruim em perguntas genéricas
    seed = _fallback_expansion(q)

    client = OpenAI()

    prompt = f"""Consulta do usuário: {q}

Gere termos úteis para buscar cláusulas contratuais relacionadas.
"""

    try:
        resp = client.responses.create(
            model=model,
            input=[
                {"role": "system", "content": [{"type": "input_text", "text": SYSTEM_PROMPT}]},
                {"role": "user", "content": [{"type": "input_text", "text": prompt}]},
            ],
            response_format={"type": "json_schema", "json_schema": EXPANSION_SCHEMA},
        )

        parsed = json.loads(resp.output_text)

        # combina IA + seeds (seed garante termos “jurídicos clássicos”)
        keywords = _clean_terms((parsed.get("keywords") or []) + (seed.get("keywords") or []), max_len=32)[:10]
        phrases = _clean_terms((parsed.get("phrases") or []) + (seed.get("phrases") or []), max_len=64)[:6]
        negative = _clean_terms(parsed.get("negative") or [], max_len=32)[:6]

        result = {"keywords": keywords, "phrases": phrases, "negative": negative}

    except Exception:
        # ✅ se a OpenAI falhar, o sistema continua funcionando
        result = seed

    cache.set(cache_key, result, 24 * 60 * 60)  # 24h
    return result
