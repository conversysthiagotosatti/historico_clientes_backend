from decimal import Decimal

from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone

from .models import Tarefa, Apontamento, Epico
from .serializers import TarefaSerializer, ApontamentoSerializer, EpicoSerializer


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

    @action(detail=False, methods=["post"], url_path="registrar-total-horas")
    def registrar_total_horas(self, request):
        """
        Registra horas em uma tarefa informando apenas o total acumulado.

        Body JSON:
        {
          "tarefa": 1,
          "total_horas": "10.5",
          "descricao": "até hoje"
        }
        """
        tarefa_id = request.data.get("tarefa")
        total_horas = request.data.get("total_horas")
        descricao = request.data.get("descricao") or ""

        if not tarefa_id or total_horas is None:
            return Response(
                {"detail": "Campos 'tarefa' e 'total_horas' são obrigatórios."},
                status=400,
            )

        try:
            tarefa = Tarefa.objects.get(pk=int(tarefa_id))
        except (Tarefa.DoesNotExist, ValueError):
            return Response({"detail": "Tarefa não encontrada."}, status=404)

        try:
            total = Decimal(str(total_horas))
        except Exception:
            return Response(
                {"detail": "total_horas inválido. Use número decimal."},
                status=400,
            )

        horas_antes = tarefa.horas_consumidas
        delta = total - horas_antes

        if delta <= 0:
            return Response(
                {
                    "detail": "total_horas deve ser maior que as horas já registradas.",
                    "horas_atuais": str(horas_antes),
                },
                status=400,
            )

        apont = Apontamento.objects.create(
            tarefa=tarefa,
            data=timezone.now().date(),
            horas=delta,
            descricao=descricao or f"Ajuste para total acumulado de {total}h",
        )

        return Response(
            {
                "id": apont.id,
                "tarefa": tarefa.id,
                "horas_antes": str(horas_antes),
                "horas_adicionadas": str(delta),
                "horas_totais": str(tarefa.horas_consumidas),
            },
            status=201,
        )


class EpicoViewSet(ModelViewSet):
    queryset = Epico.objects.select_related("contrato", "contrato__cliente").all()
    serializer_class = EpicoSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    filterset_fields = {
        "contrato": ["exact"],
        "contrato__cliente": ["exact"],
        "status": ["exact"],
        "criado_em": ["date", "date__gte", "date__lte"],
        "atualizado_em": ["date", "date__gte", "date__lte"],
    }

    search_fields = ["titulo", "descricao", "contrato__titulo", "contrato__cliente__nome"]
    ordering_fields = ["criado_em", "atualizado_em", "titulo", "status"]
    ordering = ["-criado_em"]
