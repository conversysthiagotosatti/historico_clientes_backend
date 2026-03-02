from openai import OpenAI
from django.utils import timezone
from django.db import transaction

from parametro.services import get_parametro_cliente
from contratos_ai.models import ClausulaBase, DocumentoGerado


@transaction.atomic
def gerar_contrato_por_prompt(
    cliente_id: int,
    tipo_contrato: str,
    prompt_usuario: str,
    usuario
):
    """
    Gera contrato com base em prompt e cláusulas disponíveis.
    Salva automaticamente no banco.
    """

    # 🔐 Buscar chave OpenAI do cliente
    api_key = get_parametro_cliente(str(cliente_id), "OPEN_API_KEY")

    if not api_key:
        raise Exception("Cliente não possui OPEN_API_KEY configurada.")

    client = OpenAI(api_key=api_key)

    # 🔎 Buscar cláusulas ativas
    clausulas = ClausulaBase.objects.filter(ativa=True)

    clausulas_texto = "\n\n".join(
        [f"Título: {c.titulo}\n{c.texto}" for c in clausulas]
    )

    # 🧠 Prompt estruturado
    prompt_final = f"""
Você é um advogado especialista em contratos de tecnologia.

Tipo de contrato: {tipo_contrato}

Objetivo:
{prompt_usuario}

Utilize as cláusulas abaixo como base e adapte conforme necessário:
Não é necess´ario usar todas, use o que fizer sentido para o tipo de contrato e objetivo.

{clausulas_texto}

Regras:
- Estruture com numeração jurídica
- Linguagem formal
- Não invente dados irreais
- Inclua SLA e penalidades se aplicável
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt_final}],
        temperature=0.4
    )

    contrato_gerado = response.choices[0].message.content.strip()

    # 💾 Gravar no banco
    documento = DocumentoGerado.objects.create(
        cliente_id=cliente_id,
        tipo=tipo_contrato,
        conteudo=contrato_gerado,
        prompt_usado=prompt_final,
        criado_por=usuario,
        versao=1,
        criado_em=timezone.now()
    )

    return documento