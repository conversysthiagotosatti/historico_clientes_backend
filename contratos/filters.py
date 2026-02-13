import django_filters
from .models import Contrato


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
