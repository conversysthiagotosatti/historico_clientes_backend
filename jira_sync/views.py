from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from jira_sync.models import JiraConnection, JiraProject, JiraIssue
from jira_sync.serializers import JiraConnectionSerializer, JiraProjectSerializer, JiraIssueSerializer
from jira_sync.filters import JiraConnectionFilter, JiraProjectFilter, JiraIssueFilter

# opcional (se estiver usando multi-tenant)
try:
    from accounts.tenant import get_cliente_id_from_request
except Exception:
    get_cliente_id_from_request = None


class JiraConnectionViewSet(ModelViewSet):
    serializer_class = JiraConnectionSerializer
    permission_classes = [IsAuthenticated]
    queryset = JiraConnection.objects.all()

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = JiraConnectionFilter
    search_fields = ["nome_jira", "base_url", "email", "cliente__nome"]
    ordering_fields = ["id", "atualizado_em", "criado_em"]
    ordering = ["-atualizado_em"]

    def get_queryset(self):
        qs = super().get_queryset()
        if get_cliente_id_from_request:
            cid = get_cliente_id_from_request(self.request)
            qs = qs.filter(cliente_id=cid)
        return qs

    def perform_create(self, serializer):
        if get_cliente_id_from_request:
            cid = get_cliente_id_from_request(self.request)
            serializer.save(cliente_id=cid)
        else:
            serializer.save()


class JiraProjectViewSet(ModelViewSet):
    serializer_class = JiraProjectSerializer
    permission_classes = [IsAuthenticated]
    queryset = JiraProject.objects.select_related("jira_connection", "jira_connection__cliente")

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = JiraProjectFilter
    search_fields = ["key", "name", "jira_id"]
    ordering_fields = ["id", "key", "name", "atualizado_em", "criado_em"]
    ordering = ["key"]

    def get_queryset(self):
        qs = super().get_queryset()
        if get_cliente_id_from_request:
            cid = get_cliente_id_from_request(self.request)
            qs = qs.filter(jira_connection__cliente_id=cid)
        return qs

    def perform_create(self, serializer):
        # garante que o project está sendo criado em uma connection do cliente atual
        obj = serializer.validated_data.get("jira_connection")
        if get_cliente_id_from_request:
            cid = get_cliente_id_from_request(self.request)
            if obj.cliente_id != cid:
                raise PermissionDenied("jira_connection não pertence ao cliente atual.")
        serializer.save()


class JiraIssueViewSet(ModelViewSet):
    serializer_class = JiraIssueSerializer
    permission_classes = [IsAuthenticated]
    queryset = JiraIssue.objects.select_related("cliente", "contrato", "tarefa_local")

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = JiraIssueFilter
    search_fields = ["key", "summary", "status", "project_key"]
    ordering_fields = ["jira_updated_at", "jira_created_at", "criado_em", "atualizado_em"]
    ordering = ["-jira_updated_at", "-atualizado_em"]

    def get_queryset(self):
        qs = super().get_queryset()
        if get_cliente_id_from_request:
            cid = get_cliente_id_from_request(self.request)
            qs = qs.filter(cliente_id=cid)
        return qs

    def perform_create(self, serializer):
        if get_cliente_id_from_request:
            cid = get_cliente_id_from_request(self.request)
            serializer.save(cliente_id=cid)
        else:
            serializer.save()
