from rest_framework import serializers
from jira_sync.models import JiraConnection, JiraProject, JiraIssue


class JiraConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = JiraConnection
        fields = [
            "id",
            "cliente",
            "nome_jira",
            "base_url",
            "sufixo_url",
            "cloud_id",
            "email",
            "api_token",
            "ativo",
            "criado_em",
            "atualizado_em",
        ]
        read_only_fields = ["criado_em", "atualizado_em"]

    def validate(self, attrs):
        # normaliza sufixo_url
        sufixo = attrs.get("sufixo_url")
        if sufixo:
            sufixo = sufixo.strip()
            if sufixo and not sufixo.startswith("/"):
                sufixo = "/" + sufixo
            attrs["sufixo_url"] = sufixo
        return attrs


class JiraProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = JiraProject
        fields = [
            "id",
            "jira_connection",
            "jira_id",
            "key",
            "name",
            "project_type",
            "is_private",
            "archived",
            "lead_account_id",
            "lead_display_name",
            "url",
            "raw",
            "criado_em",
            "atualizado_em",
        ]
        read_only_fields = ["criado_em", "atualizado_em"]


class JiraIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = JiraIssue
        fields = [
            "id",
            "cliente",
            "contrato",
            "jira_id",
            "key",
            "project_key",
            "issue_type",
            "summary",
            "description",
            "status",
            "priority",
            "assignee_account_id",
            "assignee_display_name",
            "reporter_account_id",
            "reporter_display_name",
            "labels",
            "components",
            "raw",
            "jira_created_at",
            "jira_updated_at",
            "jira_resolved_at",
            "due_date",
            "original_estimate_seconds",
            "time_spent_seconds",
            "tarefa_local",
            "criado_em",
            "atualizado_em",
        ]
        read_only_fields = ["criado_em", "atualizado_em"]
