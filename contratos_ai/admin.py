from django.contrib import admin, messages
from django.utils.html import format_html
from django import forms

from .models import ClausulaBase, DocumentoGerado, MemoriaCalculo, MemoriaCalculoItem
from contratos_ai.services.memoria_calculo_service import calcular_memoria
from contratos_ai.services.memoria_import_excel import importar_excel_memoria


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


# ================================
# MEMÓRIA DE CÁLCULO
# ================================


class MemoriaCalculoItemInline(admin.TabularInline):
    model = MemoriaCalculoItem
    extra = 1


class MemoriaCalculoImportForm(forms.Form):
    arquivo_excel = forms.FileField(
        required=False,
        label="Arquivo Excel (.xlsx) para importar itens",
        help_text="Selecione uma memória e envie um arquivo Excel compatível.",
    )


@admin.register(MemoriaCalculo)
class MemoriaCalculoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "contrato",
        "gross_revenue",
        "lucro",
        "margem_percentual",
        "criado_em",
    )

    search_fields = ("contrato__id", "contrato__titulo", "contrato__cliente__nome")
    list_filter = ("contrato",)

    inlines = [MemoriaCalculoItemInline]

    actions = ["recalcular_memorias", "importar_itens_de_excel"]
    actions_form = MemoriaCalculoImportForm

    @admin.action(description="Recalcular memória de cálculo")
    def recalcular_memorias(self, request, queryset):
        total = 0
        for memoria in queryset:
            calcular_memoria(memoria)
            total += 1

        self.message_user(
            request,
            f"{total} memória(s) recalculada(s) com sucesso.",
            messages.SUCCESS,
        )

    @admin.action(description="Importar itens de Excel (selecionar 1 memória)")
    def importar_itens_de_excel(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(
                request,
                "Selecione exatamente uma memória de cálculo para importar.",
                messages.ERROR,
            )
            return

        arquivo = request.FILES.get("arquivo_excel")
        if not arquivo:
            self.message_user(
                request,
                "Nenhum arquivo Excel foi enviado. Use o campo abaixo da caixa de ações.",
                messages.ERROR,
            )
            return

        memoria = queryset.first()
        try:
            importar_excel_memoria(memoria, arquivo)
        except Exception as exc:
            self.message_user(
                request,
                f"Erro ao importar Excel: {exc}",
                messages.ERROR,
            )
            return

        self.message_user(
            request,
            f"Itens importados e memória recalculada para o contrato {memoria.contrato}.",
            messages.SUCCESS,
        )
