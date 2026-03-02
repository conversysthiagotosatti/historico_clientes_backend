from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Setor,
    Chamado,
    ChamadoMensagem,
    ChamadoHistorico,
    ChamadoApontamento,
    ChamadoTimer,
)


# ================================
# 🔹 SETOR
# ================================

@admin.register(Setor)
class SetorAdmin(admin.ModelAdmin):
    list_display = ("nome", "cor_preview", "icone")
    search_fields = ("nome",)

    def cor_preview(self, obj):
        return format_html(
            '<div style="width:20px;height:20px;background:{};"></div>',
            obj.cor
        )
    cor_preview.short_description = "Cor"


# ================================
# 🔹 INLINES
# ================================

class ChamadoMensagemInline(admin.TabularInline):
    model = ChamadoMensagem
    extra = 0
    readonly_fields = ("criado_em",)
    autocomplete_fields = ("autor",)


class ChamadoHistoricoInline(admin.TabularInline):
    model = ChamadoHistorico
    extra = 0
    readonly_fields = ("criado_em",)


class ChamadoApontamentoInline(admin.TabularInline):
    model = ChamadoApontamento
    extra = 0
    readonly_fields = ("criado_em",)
    autocomplete_fields = ("atendente",)


class ChamadoTimerInline(admin.TabularInline):
    model = ChamadoTimer
    extra = 0
    readonly_fields = ("criado_em", "atualizado_em")


# ================================
# 🔹 CHAMADO
# ================================

@admin.register(Chamado)
class ChamadoAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "titulo",
        "status",
        "prioridade",
        "setor",
        "solicitante",
        "atendente",
        "criado_em",
    )

    list_filter = (
        "status",
        "prioridade",
        "setor",
        "criado_em",
    )

    search_fields = (
        "titulo",
        "descricao",
        "solicitante__username",
        "atendente__username",
    )

    autocomplete_fields = (
        "solicitante",
        "atendente",
        "setor",
        "chamados_vinculados",
    )

    readonly_fields = (
        "criado_em",
        "atualizado_em",
        "resolvido_em",
    )

    inlines = [
        ChamadoMensagemInline,
        ChamadoHistoricoInline,
        ChamadoApontamentoInline,
        ChamadoTimerInline,
    ]

    fieldsets = (
        ("Informações principais", {
            "fields": (
                "titulo",
                "descricao",
                "setor",
            )
        }),
        ("Status e Prioridade", {
            "fields": (
                "status",
                "prioridade",
                "sla_horas",
            )
        }),
        ("Usuários", {
            "fields": (
                "solicitante",
                "atendente",
            )
        }),
        ("Relacionamentos", {
            "fields": (
                "chamados_vinculados",
            )
        }),
        ("Datas", {
            "fields": (
                "criado_em",
                "atualizado_em",
                "resolvido_em",
            )
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related(
            "setor",
            "solicitante",
            "atendente",
        )


# ================================
# 🔹 REGISTROS ISOLADOS (opcional)
# ================================

@admin.register(ChamadoMensagem)
class ChamadoMensagemAdmin(admin.ModelAdmin):
    list_display = ("chamado", "autor", "tipo_autor", "criado_em")
    list_filter = ("tipo_autor", "criado_em")
    search_fields = ("conteudo",)
    autocomplete_fields = ("chamado", "autor")


@admin.register(ChamadoHistorico)
class ChamadoHistoricoAdmin(admin.ModelAdmin):
    list_display = ("chamado", "status_anterior", "status_novo", "usuario", "criado_em")
    list_filter = ("status_novo", "criado_em")
    autocomplete_fields = ("chamado", "usuario")


@admin.register(ChamadoApontamento)
class ChamadoApontamentoAdmin(admin.ModelAdmin):
    list_display = ("chamado", "atendente", "data", "horas")
    list_filter = ("data",)
    autocomplete_fields = ("chamado", "atendente")


@admin.register(ChamadoTimer)
class ChamadoTimerAdmin(admin.ModelAdmin):
    list_display = ("chamado", "atendente", "estado", "tempo_acumulado_segundos")
    list_filter = ("estado",)
    autocomplete_fields = ("chamado", "atendente")