# contratos_ai/services/clausula_ai.py

import json
from openai import OpenAI
from parametro.services import get_parametro_cliente


def gerar_clausula_json(cliente_id: int, descricao: str) -> dict:
    """
    Gera uma cláusula estruturada pronta para salvar no banco.
    """

    api_key = get_parametro_cliente(str(cliente_id), "OPEN_API_KEY")

    if not api_key:
        raise Exception("Cliente não possui OPEN_API_KEY configurada.")

    client = OpenAI(api_key=api_key)

    prompt = f"""
Você é um advogado especialista em contratos de tecnologia.

Com base na descrição abaixo, gere uma cláusula estruturada.

Descrição:
{descricao}

Retorne EXCLUSIVAMENTE um JSON no seguinte formato:

{{
  "titulo": "string",
  "tipo": "financeiro | sla | tecnica | lgpd | penalidade | rescisao | monitoramento | comercial",
  "texto": "texto completo jurídico da cláusula",
  "palavras_chave": "palavra1, palavra2, palavra3",
  "ativa": true,
  "versao": 1
}}

Não inclua explicações.
Não inclua texto fora do JSON.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )

    conteudo = response.choices[0].message.content.strip()

    try:
        clausula_json = json.loads(conteudo)
    except json.JSONDecodeError:
        raise Exception("Erro ao gerar JSON válido da cláusula.")

    return clausula_json