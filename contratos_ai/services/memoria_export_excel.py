from __future__ import annotations

import os

import openpyxl
from django.conf import settings

from contratos_ai.models import MemoriaCalculo


def exportar_memoria_excel(memoria: MemoriaCalculo) -> str:
    """
    Exporta a memória de cálculo e seus itens para um arquivo XLSX.
    Retorna o caminho absoluto do arquivo gerado.
    """

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Memória de Cálculo"

    # Cabeçalho
    ws.append(["Tipo", "Descrição", "Quantidade", "Preço Unitário", "Total"])

    for item in memoria.itens.all():
        ws.append(
            [
                item.tipo,
                item.descricao,
                item.quantidade,
                item.preco_unitario,
                item.total,
            ]
        )

    pasta = os.path.join(settings.MEDIA_ROOT, "memorias_calculo")
    os.makedirs(pasta, exist_ok=True)

    caminho = os.path.join(pasta, f"memoria_{memoria.id}.xlsx")
    wb.save(caminho)

    return caminho

