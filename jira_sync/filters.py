import django_filters
from jira_sync.models import JiraConnection, JiraProject, JiraIssue


class JiraConnectionFilter(django_filters.FilterSet):
    cliente = django_filters.NumberFilter(field_name="cliente_id")
    ativo = django_filters.BooleanFilter(field_name="ativo")

    class Meta:
        model = JiraConnection
        fields = ["cliente", "ativo"]


class JiraProjectFilter(django_filters.FilterSet):
    jira_connection = django_filters.NumberFilter(field_name="jira_connection_id")
    archived = django_filters.BooleanFilter(field_name="archived")
    key = django_filters.CharFilter(field_name="key", lookup_expr="iexact")
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = JiraProject
        fields = ["jira_connection", "archived", "key", "name"]


class JiraIssueFilter(django_filters.FilterSet):
    cliente = django_filters.NumberFilter(field_name="cliente_id")
    contrato = django_filters.NumberFilter(field_name="contrato_id")

    # ✅ novos
    project = django_filters.NumberFilter(field_name="project_id")
    is_subtask = django_filters.BooleanFilter(field_name="is_subtask")
    parent_issue = django_filters.NumberFilter(field_name="parent_issue_id")

    project_key = django_filters.CharFilter(field_name="project_key", lookup_expr="iexact")
    status = django_filters.CharFilter(field_name="status", lookup_expr="iexact")
    key = django_filters.CharFilter(field_name="key", lookup_expr="iexact")
    summary = django_filters.CharFilter(field_name="summary", lookup_expr="icontains")

    class Meta:
        model = JiraIssue
        fields = ["cliente", "contrato", "project", "is_subtask", "parent_issue", "project_key", "status", "key", "summary"]
