import django_filters
from .models import Contrato, ContratoTarefa, ContratoClausula

class ContratoFilter(django_filters.FilterSet):
    # filtro por cliente (id)
    cliente = django_filters.NumberFilter(field_name="cliente_id")

    # filtros por data (intervalo)
    data_inicio_de = django_filters.DateFilter(field_name="data_inicio", lookup_expr="gte")
    data_inicio_ate = django_filters.DateFilter(field_name="data_inicio", lookup_expr="lte")

    data_fim_de = django_filters.DateFilter(field_name="data_fim", lookup_expr="gte")
    data_fim_ate = django_filters.DateFilter(field_name="data_fim", lookup_expr="lte")

    # filtro texto
    titulo = django_filters.CharFilter(field_name="titulo", lookup_expr="icontains")

    # filtro por horas
    horas_min = django_filters.NumberFilter(field_name="horas_previstas_total", lookup_expr="gte")
    horas_max = django_filters.NumberFilter(field_name="horas_previstas_total", lookup_expr="lte")

    # opcional: contratos ativos na data X (ex: hoje)
    ativo_em = django_filters.DateFilter(method="filter_ativo_em")

    def filter_ativo_em(self, queryset, name, value):
        # ativo se data_inicio <= value e (data_fim is null ou data_fim >= value)
        return queryset.filter(data_inicio__lte=value).filter(
            django_filters.filters.Q(data_fim__isnull=True) | django_filters.filters.Q(data_fim__gte=value)
        )

    class Meta:
        model = Contrato
        fields = [
            "cliente",
            "titulo",
            "data_inicio_de",
            "data_inicio_ate",
            "data_fim_de",
            "data_fim_ate",
            "horas_min",
            "horas_max",
            "ativo_em",
        ]

class ContratoTarefaFilter(django_filters.FilterSet):
    # filtros por data (intervalo)
    criado_em_de = django_filters.DateTimeFilter(field_name="criado_em", lookup_expr="gte")
    criado_em_ate = django_filters.DateTimeFilter(field_name="criado_em", lookup_expr="lte")
    atualizado_em_de = django_filters.DateTimeFilter(field_name="atualizado_em", lookup_expr="gte")
    atualizado_em_ate = django_filters.DateTimeFilter(field_name="atualizado_em", lookup_expr="lte")

    # filtros por campos relacionados
    cliente = django_filters.NumberFilter(field_name="contrato__cliente_id")
    contrato = django_filters.NumberFilter(field_name="contrato_id")
    clausula = django_filters.NumberFilter(field_name="clausula_id")

    # filtros diretos
    status = django_filters.CharFilter(field_name="status")
    prioridade = django_filters.CharFilter(field_name="prioridade", lookup_expr="iexact")
    gerada_por_ia = django_filters.BooleanFilter(field_name="gerada_por_ia")
    responsavel_sugerido = django_filters.CharFilter(field_name="responsavel_sugerido", lookup_expr="icontains")

    class Meta:
        model = ContratoTarefa
        fields = [
            "cliente",
            "contrato",
            "clausula",
            "status",
            "prioridade",
            "gerada_por_ia",
            "responsavel_sugerido",
            "criado_em_de",
            "criado_em_ate",
            "atualizado_em_de",
            "atualizado_em_ate",
        ]



class ContratoClausulaFilter(django_filters.FilterSet):
    # IDs
    contrato = django_filters.NumberFilter(field_name="contrato_id")
    fonte_arquivo = django_filters.NumberFilter(field_name="fonte_arquivo_id")

    # booleans
    extraida_por_ia = django_filters.BooleanFilter(field_name="extraida_por_ia")

    # numero
    numero = django_filters.CharFilter(field_name="numero", lookup_expr="exact")
    numero_contains = django_filters.CharFilter(field_name="numero", lookup_expr="icontains")

    # texto/titulo
    titulo = django_filters.CharFilter(field_name="titulo", lookup_expr="icontains")
    texto = django_filters.CharFilter(field_name="texto", lookup_expr="icontains")

    # ordem (range)
    ordem_min = django_filters.NumberFilter(field_name="ordem", lookup_expr="gte")
    ordem_max = django_filters.NumberFilter(field_name="ordem", lookup_expr="lte")

    # confidence (range)
    confidence_min = django_filters.NumberFilter(field_name="confidence", lookup_expr="gte")
    confidence_max = django_filters.NumberFilter(field_name="confidence", lookup_expr="lte")

    # datas (range)
    criado_de = django_filters.DateTimeFilter(field_name="criado_em", lookup_expr="gte")
    criado_ate = django_filters.DateTimeFilter(field_name="criado_em", lookup_expr="lte")
    atualizado_de = django_filters.DateTimeFilter(field_name="atualizado_em", lookup_expr="gte")
    atualizado_ate = django_filters.DateTimeFilter(field_name="atualizado_em", lookup_expr="lte")

    class Meta:
        model = ContratoClausula
        fields = []