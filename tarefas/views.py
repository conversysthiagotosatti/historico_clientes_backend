from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Tarefa, Apontamento
from .serializers import TarefaSerializer, ApontamentoSerializer

class TarefaViewSet(ModelViewSet):
    queryset = Tarefa.objects.select_related("contrato", "contrato__cliente").all()
    serializer_class = TarefaSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    # ✅ filtros (inclui cliente via relacionamento)
    filterset_fields = {
        "contrato": ["exact"],                 # ?contrato=10
        "contrato__cliente": ["exact"],         # ?contrato__cliente=1  (filtro por cliente)
        "status": ["exact"],                   # ?status=ABERTA
        "criado_em": ["date", "date__gte", "date__lte"],
        "atualizado_em": ["date", "date__gte", "date__lte"],
    }

    # 🔍 busca
    search_fields = ["titulo", "descricao", "contrato__titulo", "contrato__cliente__nome"]

    # ↕️ ordenação
    ordering_fields = ["criado_em", "atualizado_em", "horas_previstas", "titulo", "status"]
    ordering = ["-criado_em"]


class ApontamentoViewSet(ModelViewSet):
    queryset = Apontamento.objects.select_related(
        "tarefa", "tarefa__contrato", "tarefa__contrato__cliente"
    ).all()
    serializer_class = ApontamentoSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    # ✅ filtros (inclui por cliente e contrato)
    filterset_fields = {
        "tarefa": ["exact"],                    # ?tarefa=5
        "tarefa__contrato": ["exact"],          # ?tarefa__contrato=10
        "tarefa__contrato__cliente": ["exact"], # ?tarefa__contrato__cliente=1 (cliente)
        "data": ["exact", "gte", "lte"],        # ?data__gte=2026-02-01&data__lte=2026-02-28
        "criado_em": ["date", "date__gte", "date__lte"],
    }

    search_fields = ["descricao", "tarefa__titulo"]
    ordering_fields = ["data", "horas", "criado_em"]
    ordering = ["-data", "-criado_em"]
