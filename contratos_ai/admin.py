from django.contrib import admin
from django.utils.html import format_html
from .models import ClausulaBase, DocumentoGerado
from django.utils.html import format_html


# ================================
# CLAUSULA BASE
# ================================

@admin.register(ClausulaBase)
class ClausulaBaseAdmin(admin.ModelAdmin):
    list_display = (
        "titulo",
        "tipo",
        "versao",
        "ativa",
        "criada_em",
    )

    list_filter = (
        "tipo",
        "ativa",
        "criada_em",
    )

    search_fields = (
        "titulo",
        "texto",
        "palavras_chave",
    )

    ordering = ("-criada_em",)

    readonly_fields = ("criada_em",)

    fieldsets = (
        ("Informações Gerais", {
            "fields": ("titulo", "tipo", "versao", "ativa")
        }),
        ("Conteúdo da Cláusula", {
            "fields": ("texto",)
        }),
        ("Palavras-chave", {
            "fields": ("palavras_chave",),
            "description": "Separe as palavras por vírgula"
        }),
        ("Auditoria", {
            "fields": ("criada_em",)
        }),
    )


# ================================
# DOCUMENTO GERADO
# ================================

@admin.register(DocumentoGerado)
class DocumentoGeradoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "cliente",
        "tipo",
        "versao",
        "criado_por",
        "criado_em",
    )

    list_filter = (
        "tipo",
        "criado_em",
        "cliente",
    )

    search_fields = (
        "cliente__nome",
        "conteudo",
    )

    ordering = ("-criado_em",)

    readonly_fields = (
        "prompt_usado",
        "conteudo",
        "criado_em",
    )

    fieldsets = (
        ("Informações Gerais", {
            "fields": ("cliente", "tipo", "versao", "criado_por")
        }),
        ("Documento Gerado", {
            "fields": ("conteudo",)
        }),
        ("Prompt Utilizado (Auditoria IA)", {
            "fields": ("prompt_usado",),
            "classes": ("collapse",)
        }),
        ("Auditoria", {
            "fields": ("criado_em",)
        }),
    )

def preview_documento(self, obj):
    return format_html(
        "<span style='color: {};'>✔ Gerado</span>",
        "green"
    )