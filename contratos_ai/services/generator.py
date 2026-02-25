from openai import OpenAI
from parametro.services import get_parametro_cliente


def gerar_documento(cliente_id, tipo, contexto_extra):

    # 🔐 pega chave por cliente
    api_key = get_parametro_cliente(str(cliente_id), "OPEN_API_KEY")

    if not api_key:
        raise Exception("Cliente não possui OPEN_API_KEY configurada.")

    # instancia client aqui
    client = OpenAI(api_key=api_key)

    prompt = f"""
Você é um advogado especialista em contratos de TI.

Contexto:
{contexto_extra}

Gere um {tipo} completo, estruturado e profissional.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content, prompt