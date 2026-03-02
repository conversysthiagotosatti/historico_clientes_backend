from openai import OpenAI

def gerar_resumo_executivo(dados: dict) -> str:

    client = OpenAI()

    prompt = f"""
    Gere um resumo executivo para diretoria com base nos seguintes indicadores:

    SLA Geral: {dados['sla_geral']}%
    Disponibilidade Média: {dados['disponibilidade_media']}%
    Total de Incidentes: {dados['total_incidentes']}
    Eventos Críticos: {dados['eventos_criticos']}
    MTTR Médio (min): {dados['mttr_medio_minutos']}

    Destaque riscos, pontos fortes e recomendações estratégicas.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content