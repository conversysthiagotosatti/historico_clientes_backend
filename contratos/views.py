from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Contrato
from .serializers import ContratoSerializer

class ContratoViewSet(ModelViewSet):
    queryset = Contrato.objects.select_related("cliente").all()
    serializer_class = ContratoSerializer

    # 🔎 Filtros
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    # ✅ filtro por cliente e outros campos
    filterset_fields = {
        "cliente": ["exact"],                 # ?cliente=1
        "data_inicio": ["exact", "gte", "lte"],# ?data_inicio__gte=2026-01-01
        "data_fim": ["exact", "gte", "lte", "isnull"], # ?data_fim__isnull=true
    }

    # 🔍 busca textual
    search_fields = ["titulo", "descricao", "cliente__nome"]

    # ↕️ ordenação
    ordering_fields = ["criado_em", "data_inicio", "data_fim", "horas_previstas_total", "titulo"]
    ordering = ["-criado_em"]
