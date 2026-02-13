# jira_sync/admin.py
from django.contrib import admin
from .models import JiraConnection, JiraProject, JiraIssue


# ---------- Inlines ----------

class JiraProjectInline(admin.TabularInline):
    model = JiraProject
    extra = 0
    fields = (
        "contrato",
        "key",
        "name",
        "project_type",
        "archived",
        "is_private",
        "atualizado_em",
    )
    readonly_fields = ("atualizado_em",)
    autocomplete_fields = ("contrato",)
    show_change_link = True


class JiraSubtaskInline(admin.TabularInline):
    """
    Mostra subtasks dentro da issue pai.
    """
    model = JiraIssue
    fk_name = "parent_issue"
    extra = 0
    fields = ("key", "summary", "status", "priority", "assignee_display_name", "jira_updated_at")
    readonly_fields = ("jira_updated_at",)
    show_change_link = True


# ---------- Admins ----------

@admin.register(JiraConnection)
class JiraConnectionAdmin(admin.ModelAdmin):
    list_display = ("id", "cliente", "nome_jira", "base_url", "cloud_id", "email", "ativo", "atualizado_em")
    list_filter = ("ativo",)
    search_fields = ("cliente__nome", "nome_jira", "base_url", "email", "cloud_id")
    ordering = ("-atualizado_em",)
    autocomplete_fields = ("cliente",)
    readonly_fields = ("criado_em", "atualizado_em")
    inlines = [JiraProjectInline]

    fieldsets = (
        ("Cliente", {"fields": ("cliente", "nome_jira", "ativo")}),
        ("Conexão", {"fields": ("base_url", "sufixo_url", "cloud_id", "email", "api_token")}),
        ("Auditoria", {"fields": ("criado_em", "atualizado_em")}),
    )


@admin.register(JiraProject)
class JiraProjectAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "jira_connection",
        "contrato",
        "key",
        "name",
        "project_type",
        "archived",
        "is_private",
        "atualizado_em",
    )
    list_filter = (
        "jira_connection",
        "contrato",
        "archived",
        "is_private",
        "project_type",
    )
    search_fields = (
        "key",
        "name",
        "jira_id",
        "jira_connection__cliente__nome",
        "jira_connection__nome_jira",
        "contrato__titulo",
        "contrato__cliente__nome",
    )
    ordering = ("key",)
    autocomplete_fields = ("jira_connection", "contrato")
    readonly_fields = ("criado_em", "atualizado_em")

    fieldsets = (
        ("Vínculos", {"fields": ("jira_connection", "contrato")}),
        ("Identificadores Jira", {"fields": ("jira_id", "key", "name")}),
        ("Configuração", {"fields": ("project_type", "archived", "is_private", "url")}),
        ("Líder", {"fields": ("lead_account_id", "lead_display_name")}),
        ("Extras", {"fields": ("raw",)}),
        ("Auditoria", {"fields": ("criado_em", "atualizado_em")}),
    )


@admin.register(JiraIssue)
class JiraIssueAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "cliente",
        "contrato",
        "project",
        "key",
        "issue_type",
        "is_subtask",
        "parent_issue",
        "status",
        "priority",
        "assignee_display_name",
        "jira_updated_at",
    )
    list_filter = (
        "cliente",
        "contrato",
        "project",
        "is_subtask",
        "status",
        "priority",
        "issue_type",
    )
    search_fields = (
        "key",
        "summary",
        "project_key",
        "cliente__nome",
        "contrato__titulo",
        "assignee_display_name",
        "reporter_display_name",
    )
    ordering = ("-jira_updated_at", "-atualizado_em")
    autocomplete_fields = ("cliente", "contrato", "project", "parent_issue", "tarefa_local")
    readonly_fields = ("criado_em", "atualizado_em")

    inlines = [JiraSubtaskInline]

    fieldsets = (
        ("Identificação / Vínculos", {"fields": ("cliente", "contrato", "project")}),
        ("Jira", {"fields": ("jira_id", "key", "project_key", "issue_type_id", "issue_type")}),
        ("Conteúdo", {"fields": ("summary", "description")}),
        ("Status", {"fields": ("status", "priority")}),
        ("Responsáveis", {"fields": ("assignee_account_id", "assignee_display_name", "reporter_account_id", "reporter_display_name")}),
        ("Hierarquia", {"fields": ("is_subtask", "parent_issue", "parent_key")}),
        ("Datas", {"fields": ("jira_created_at", "jira_updated_at", "jira_resolved_at", "due_date")}),
        ("Tempo", {"fields": ("original_estimate_seconds", "time_spent_seconds")}),
        ("Integração com App", {"fields": ("tarefa_local",)}),
        ("Extras", {"fields": ("labels", "components", "raw")}),
        ("Auditoria", {"fields": ("criado_em", "atualizado_em")}),
    )
