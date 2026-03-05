from decimal import Decimal


def calcular_memoria(memoria):
    """
    Recalcula todos os totais da memória de cálculo a partir dos itens.
    """

    total_receita = Decimal("0")
    total_custo = Decimal("0")
    total_opex = Decimal("0")

    for item in memoria.itens.all():
        # total do item
        item.total = (item.quantidade or 0) * (item.preco_unitario or 0)
        item.save()

        if item.tipo == "receita":
            total_receita += Decimal(item.total)
        elif item.tipo == "custo":
            total_custo += Decimal(item.total)
        elif item.tipo == "opex":
            total_opex += Decimal(item.total)

    memoria.gross_revenue = total_receita
    memoria.cost_products = total_custo
    memoria.additional_costs = total_opex

    memoria.gross_profit = total_receita - total_custo
    memoria.lucro = memoria.gross_profit - total_opex

    if total_receita > 0:
        memoria.margem_percentual = (memoria.lucro / total_receita) * 100

    memoria.save()

    return memoria