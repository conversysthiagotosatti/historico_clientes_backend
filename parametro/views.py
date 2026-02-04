from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from .models import Parametro, ParametroCliente, ItensMonitoramento
from .serializers import (
    ParametroSerializer,
    ParametroClienteSerializer,
    ItensMonitoramentoSerializer
)

class ParametroViewSet(ModelViewSet):
    queryset = Parametro.objects.all().order_by("-criado_em")
    serializer_class = ParametroSerializer
    permission_classes = [IsAuthenticated]


class ParametroClienteViewSet(ModelViewSet):
    queryset = ParametroCliente.objects.select_related("cliente").all().order_by("-criado_em")
    serializer_class = ParametroClienteSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["cliente"]  # ✅ ?cliente=1


class ItensMonitoramentoViewSet(ModelViewSet):
    queryset = ItensMonitoramento.objects.select_related("cliente").all().order_by("-criado_em")
    serializer_class = ItensMonitoramentoSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["cliente", "tipo"]  # ✅ ?cliente=1&tipo=Grafico
