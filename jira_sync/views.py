import requests 

from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import JiraConnection, JiraIssue
from .serializers import JiraConnectionSerializer, JiraIssueSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny  # pode trocar depois

from jira_sync.services.jira_api import listar_projetos_jira
from urllib.parse import urljoin
from parametro.services import get_parametro_cliente, get_sufixo_api_jira, get_prefixo_api_jira


class JiraConnectionViewSet(ModelViewSet):
    queryset = JiraConnection.objects.select_related("cliente").all()
    serializer_class = JiraConnectionSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = {"cliente": ["exact"], "ativo": ["exact"]}
    search_fields = ["cliente__nome", "base_url", "email"]
    ordering_fields = ["criado_em", "atualizado_em"]
    ordering = ["-atualizado_em"]


class JiraIssueViewSet(ModelViewSet):
    queryset = JiraIssue.objects.select_related("cliente", "contrato", "tarefa_local").all()
    serializer_class = JiraIssueSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = {
        # ✅ filtros principais
        "cliente": ["exact"],                 # ?cliente=1
        "contrato": ["exact", "isnull"],      # ?contrato=10
        "status": ["exact"],                  # ?status=Done
        "project_key": ["exact"],             # ?project_key=ENG
        "issue_type": ["exact"],              # ?issue_type=Task
        "priority": ["exact"],                # ?priority=High
        "assignee_account_id": ["exact", "isnull"],
        "due_date": ["exact", "gte", "lte"],

        # por datas do Jira
        "jira_updated_at": ["date", "date__gte", "date__lte"],
        "jira_created_at": ["date", "date__gte", "date__lte"],
    }

    search_fields = ["key", "summary", "description", "assignee_display_name", "reporter_display_name"]
    ordering_fields = ["jira_updated_at", "jira_created_at", "due_date", "time_spent_seconds", "original_estimate_seconds", "criado_em"]
    ordering = ["-jira_updated_at", "-criado_em"]

def montar_url_jira(base_url: str, cloud_id: str, sufixo_url: str) -> str:
    """
    Monta a URL final da API do Jira Cloud (OAuth2).
    """
    base = f"{base_url.rstrip('/')}/{cloud_id}/"
    return urljoin(base, sufixo_url.lstrip("/"))

def listar_projetos_jira(access_token: str):
    """
    Consome a API do Jira Cloud (OAuth2) e retorna os projetos.
    """
    base_url = get_prefixo_api_jira("1", "PROJ_CLIENTES", default="/rest/api/3") #"https://api.atlassian.com/ex/jira"
    cloud_id = get_parametro_cliente("1", "Jira_Id") #"f57354ee-1d8f-4cbb-90bf-44900ed06ea1"
    sufixo_url = get_sufixo_api_jira("1", "PROJ_CLIENTES", default="/rest/api/3") #"/rest/api/3/project/search"

    #access_token = get_parametro_cliente("1", "TOKEN_JIRA")
    print(access_token)

    url = montar_url_jira(base_url, cloud_id, sufixo_url)

    print(url)

    #access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzcwNjQxMjQ2LCJpYXQiOjE3NzA2Mzk0NDYsImp0aSI6ImFmMmFlYjBjMzc3MTQ1NDhiNDJkMjYxMGFmMDU3YjkzIiwidXNlcl9pZCI6IjEifQ.lP5rzZ-7vDw9BXSOW25MWfolQilZ5bU1BYsYW6gkzo8"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }

    response = requests.get(url, headers=headers, timeout=30)

    if response.status_code != 200:
        raise Exception(
            f"Erro ao consultar Jira: {response.status_code} - {response.text}"
        )

    return response.json()

class JiraProjectsView(APIView):
    """
    POST /api/jira/projects/
    Body:
    {
        "access_token": "xxxxx"
    }
    """

    permission_classes = [AllowAny]

    def post(self, request):
        #access_token = request.data.get("access_token")
        access_token = get_parametro_cliente("1", "TOKEN_JIRA")
        if not access_token:
            return Response(
                {"detail": "Campo 'access_token' é obrigatório"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            data = listar_projetos_jira(access_token)
            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
