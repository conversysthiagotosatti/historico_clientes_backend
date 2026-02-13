from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Contrato
from .serializers import ContratoSerializer
from .filters import ContratoFilter


class ContratoViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ContratoSerializer
    queryset = Contrato.objects.select_related("cliente").all()

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ContratoFilter

    search_fields = ["titulo", "descricao", "cliente__nome"]
    ordering_fields = ["data_inicio", "data_fim", "horas_previstas_total", "atualizado_em", "criado_em"]
    ordering = ["-atualizado_em"]
