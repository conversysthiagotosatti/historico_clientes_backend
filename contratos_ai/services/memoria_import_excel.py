from __future__ import annotations

from typing import Union

import pandas as pd

from contratos_ai.models import MemoriaCalculo, MemoriaCalculoItem
from contratos_ai.services.memoria_calculo_service import calcular_memoria


def importar_excel_memoria(
    memoria: MemoriaCalculo,
    arquivo: Union[str, bytes],
) -> MemoriaCalculo:
    """
    Importa itens de uma planilha Excel para a memória de cálculo.

    Espera colunas ao menos:
      - tipo          (receita/custo/opex)
      - descricao
      - quantidade
      - preco         (preço unitário)
    """

    df = pd.read_excel(arquivo)

    # Normaliza nomes de colunas para lower sem espaços
    df.columns = [str(c).strip().lower() for c in df.columns]

    col_tipo = "tipo"
    col_desc = "descricao"
    col_qtd = "quantidade"
    col_preco = "preco"

    missing = [c for c in [col_tipo, col_desc, col_qtd, col_preco] if c not in df.columns]
    if missing:
        raise ValueError(f"Colunas obrigatórias ausentes na planilha: {', '.join(missing)}")

    itens = []
    for _, row in df.iterrows():
        tipo = str(row[col_tipo]).strip().lower()
        if not tipo:
            continue

        itens.append(
            MemoriaCalculoItem(
                memoria=memoria,
                tipo=tipo,
                descricao=str(row[col_desc]).strip(),
                quantidade=row[col_qtd] or 0,
                preco_unitario=row[col_preco] or 0,
            )
        )

    if itens:
        MemoriaCalculoItem.objects.bulk_create(itens)

    # Recalcula totais da memória
    calcular_memoria(memoria)

    return memoria

