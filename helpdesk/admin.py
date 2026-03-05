from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Chamado, ChamadoMensagem, ChamadoHistorico, ChamadoApontamento, ChamadoTimer,
    Cidade, Empresa, ClienteHelpdesk, Departamento, Filial,
    UsuarioHelpdesk, ContratoHelpdesk, AnexoContrato, Atendente,
    AtividadeChamado, AnexoChamado,
    Categoria, Servico, PrioridadeHelpdesk, StatusChamadoConfig,
    TipoChamado, Area, GrupoSolucao, Impacto, TemaTemplate, TemplateChamado,
    ItemConfiguracao, CampoCustomizavelIC, ValorCampoIC,
    Fornecedor, CentroCusto,
    FAQ, AnexoFAQ,
    Ligacao, PesquisaSatisfacao, ContestacaoChamado, FechamentoAvaliacao,
    FormularioAprovacao, CampoFormulario, ConfiguracaoAnexo,
)




# ================================
# 🔹 CHAMADO + INLINES
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

class AtividadeChamadoInline(admin.TabularInline):
    model = AtividadeChamado
    extra = 0
    readonly_fields = ("criado_em",)

class AnexoChamadoInline(admin.TabularInline):
    model = AnexoChamado
    extra = 0
    readonly_fields = ("criado_em",)


@admin.register(Chamado)
class ChamadoAdmin(admin.ModelAdmin):
    list_display = (
        "id", "titulo", "status", "prioridade", "grupo_solucao",
        "categoria", "tipo_chamado", "cliente_helpdesk",
        "solicitante", "atendente", "criado_em",
    )
    list_filter = (
        "status", "prioridade", "grupo_solucao", "categoria",
        "tipo_chamado", "area", "criado_em",
    )
    search_fields = (
        "titulo", "descricao",
        "solicitante__username", "atendente__username",
    )
    autocomplete_fields = (
        "solicitante", "atendente", "chamados_vinculados",
        "categoria", "servico", "tipo_chamado", "template",
        "area", "cliente_helpdesk", "filial", "contrato_helpdesk",
        "centro_custo", "impacto", "grupo_solucao", "atendente_helpdesk",
    )
    readonly_fields = ("criado_em", "atualizado_em", "resolvido_em")

    inlines = [
        ChamadoMensagemInline, ChamadoHistoricoInline,
        ChamadoApontamentoInline, ChamadoTimerInline,
        AtividadeChamadoInline, AnexoChamadoInline,
    ]

    fieldsets = (
        ("Informações principais", {
            "fields": ("titulo", "descricao")
        }),
        ("Classificação", {
            "fields": (
                "status", "prioridade", "tipo_chamado",
                "categoria", "servico", "area",
                "impacto", "grupo_solucao",
            )
        }),
        ("Template", {
            "fields": ("template",),
            "classes": ("collapse",),
        }),
        ("Usuários", {
            "fields": ("solicitante", "atendente", "atendente_helpdesk")
        }),
        ("Cliente / Filial / Contrato", {
            "fields": (
                "cliente_helpdesk", "filial",
                "contrato_helpdesk", "centro_custo",
            )
        }),
        ("Relacionamentos", {
            "fields": ("chamados_vinculados",),
            "classes": ("collapse",),
        }),
        ("SLA / Datas", {
            "fields": ("sla_horas", "criado_em", "atualizado_em", "resolvido_em")
        }),
        ("Integração", {
            "fields": ("codigo_integracao",),
            "classes": ("collapse",),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "solicitante", "atendente",
            "categoria", "tipo_chamado", "cliente_helpdesk", "grupo_solucao",
        )


# ================================
# 🔹 REGISTROS ISOLADOS (Chamado)
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


# ================================
# 🔹 CIDADE
# ================================
@admin.register(Cidade)
class CidadeAdmin(admin.ModelAdmin):
    list_display = ("nome", "estado", "pais", "codigo_integracao")
    search_fields = ("nome", "estado")
    list_filter = ("estado", "pais")


# ================================
# 🔹 EMPRESA
# ================================
@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ("razao_social", "nome_fantasia", "cnpj", "cidade", "ativo")
    search_fields = ("razao_social", "nome_fantasia", "cnpj")
    list_filter = ("ativo",)
    autocomplete_fields = ("cidade",)


# ================================
# 🔹 CLIENTE HELPDESK
# ================================
@admin.register(ClienteHelpdesk)
class ClienteHelpdeskAdmin(admin.ModelAdmin):
    list_display = ("razao_social", "nome_fantasia", "cnpj", "cpf", "email", "ativo", "pendencia_financeira")
    search_fields = ("razao_social", "nome_fantasia", "cnpj", "cpf", "email")
    list_filter = ("ativo", "pendencia_financeira")
    autocomplete_fields = ("cidade", "empresa", "cliente_conversys")


# ================================
# 🔹 DEPARTAMENTO
# ================================
@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ("nome", "ativo", "codigo_integracao")
    search_fields = ("nome",)
    list_filter = ("ativo",)


# ================================
# 🔹 FILIAL
# ================================
@admin.register(Filial)
class FilialAdmin(admin.ModelAdmin):
    list_display = ("nome", "cliente", "cidade", "ativo")
    search_fields = ("nome",)
    list_filter = ("ativo",)
    autocomplete_fields = ("cidade", "cliente")


# ================================
# 🔹 USUÁRIO HELPDESK
# ================================
@admin.register(UsuarioHelpdesk)
class UsuarioHelpdeskAdmin(admin.ModelAdmin):
    list_display = ("nome", "email", "perfil", "departamento", "filial", "ativo")
    search_fields = ("nome", "email", "login")
    list_filter = ("perfil", "ativo")
    autocomplete_fields = ("user", "departamento", "filial", "cliente")


# ================================
# 🔹 CONTRATO HELPDESK
# ================================
class AnexoContratoInline(admin.TabularInline):
    model = AnexoContrato
    extra = 0
    readonly_fields = ("criado_em",)

@admin.register(ContratoHelpdesk)
class ContratoHelpdeskAdmin(admin.ModelAdmin):
    list_display = ("numero", "descricao", "cliente", "data_inicio", "data_fim", "ativo")
    search_fields = ("numero", "descricao")
    list_filter = ("ativo",)
    autocomplete_fields = ("cliente", "fornecedor")
    inlines = [AnexoContratoInline]


# ================================
# 🔹 ATENDENTE
# ================================
@admin.register(Atendente)
class AtendenteAdmin(admin.ModelAdmin):
    list_display = ("nome", "email", "ativo")
    search_fields = ("nome", "email")
    list_filter = ("ativo",)
    autocomplete_fields = ("user",)


# ================================
# 🔹 ATIVIDADE DE CHAMADO
# ================================
@admin.register(AtividadeChamado)
class AtividadeChamadoAdmin(admin.ModelAdmin):
    list_display = ("id", "chamado", "tipo_atividade", "atendente", "tempo_gasto_minutos", "criado_em")
    list_filter = ("tipo_atividade", "publico", "criado_em")
    search_fields = ("descricao",)
    autocomplete_fields = ("chamado", "atendente", "usuario")


# ================================
# 🔹 ANEXO DE CHAMADO
# ================================
@admin.register(AnexoChamado)
class AnexoChamadoAdmin(admin.ModelAdmin):
    list_display = ("nome_original", "chamado", "tamanho_bytes", "mime_type", "criado_em")
    list_filter = ("mime_type", "criado_em")
    search_fields = ("nome_original",)
    autocomplete_fields = ("chamado",)


# ================================
# 🔹 CATÁLOGO
# ================================
@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nome", "categoria_pai", "ativo")
    search_fields = ("nome",)
    list_filter = ("ativo",)
    autocomplete_fields = ("categoria_pai",)

@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ("nome", "categoria", "ativo")
    search_fields = ("nome",)
    list_filter = ("ativo",)
    autocomplete_fields = ("categoria",)

@admin.register(PrioridadeHelpdesk)
class PrioridadeHelpdeskAdmin(admin.ModelAdmin):
    list_display = ("nome", "valor", "cor_preview", "ativo")
    search_fields = ("nome",)
    list_filter = ("ativo",)

    def cor_preview(self, obj):
        return format_html(
            '<div style="width:20px;height:20px;background:{};border-radius:4px;"></div>',
            obj.cor
        )
    cor_preview.short_description = "Cor"

@admin.register(StatusChamadoConfig)
class StatusChamadoConfigAdmin(admin.ModelAdmin):
    list_display = ("nome", "cor_preview", "eh_fechamento", "ativo")
    search_fields = ("nome",)
    list_filter = ("eh_fechamento", "ativo")

    def cor_preview(self, obj):
        return format_html(
            '<div style="width:20px;height:20px;background:{};border-radius:4px;"></div>',
            obj.cor
        )
    cor_preview.short_description = "Cor"

@admin.register(TipoChamado)
class TipoChamadoAdmin(admin.ModelAdmin):
    list_display = ("nome", "ativo")
    search_fields = ("nome",)
    list_filter = ("ativo",)

@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ("nome", "ativo")
    search_fields = ("nome",)
    list_filter = ("ativo",)

@admin.register(GrupoSolucao)
class GrupoSolucaoAdmin(admin.ModelAdmin):
    list_display = ("nome", "ativo")
    search_fields = ("nome",)
    list_filter = ("ativo",)

@admin.register(Impacto)
class ImpactoAdmin(admin.ModelAdmin):
    list_display = ("nome", "nivel", "ativo")
    search_fields = ("nome",)
    list_filter = ("ativo",)

@admin.register(TemaTemplate)
class TemaTemplateAdmin(admin.ModelAdmin):
    list_display = ("nome", "ativo")
    search_fields = ("nome",)
    list_filter = ("ativo",)

@admin.register(TemplateChamado)
class TemplateChamadoAdmin(admin.ModelAdmin):
    list_display = ("nome", "categoria", "servico", "tipo", "ativo")
    search_fields = ("nome",)
    list_filter = ("ativo",)
    autocomplete_fields = ("categoria", "servico", "tipo", "tema")


# ================================
# 🔹 ITEM DE CONFIGURAÇÃO
# ================================
class ValorCampoICInline(admin.TabularInline):
    model = ValorCampoIC
    extra = 0

@admin.register(ItemConfiguracao)
class ItemConfiguracaoAdmin(admin.ModelAdmin):
    list_display = ("nome", "numero_serie", "tipo", "marca", "modelo", "cliente", "ativo")
    search_fields = ("nome", "numero_serie", "marca", "modelo")
    list_filter = ("ativo", "tipo")
    autocomplete_fields = ("cliente", "filial", "departamento")
    inlines = [ValorCampoICInline]

@admin.register(CampoCustomizavelIC)
class CampoCustomizavelICAdmin(admin.ModelAdmin):
    list_display = ("nome", "tipo_campo", "obrigatorio", "ativo")
    search_fields = ("nome",)
    list_filter = ("tipo_campo", "obrigatorio", "ativo")


# ================================
# 🔹 FORNECEDOR
# ================================
@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    list_display = ("razao_social", "nome_fantasia", "cnpj", "email", "area", "ativo")
    search_fields = ("razao_social", "nome_fantasia", "cnpj", "email")
    list_filter = ("ativo",)
    autocomplete_fields = ("cidade", "area")


# ================================
# 🔹 CENTRO DE CUSTO
# ================================
@admin.register(CentroCusto)
class CentroCustoAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nome", "ativo")
    search_fields = ("nome", "codigo")
    list_filter = ("ativo",)


# ================================
# 🔹 BASE DE CONHECIMENTO (FAQ)
# ================================
class AnexoFAQInline(admin.TabularInline):
    model = AnexoFAQ
    extra = 0
    readonly_fields = ("criado_em",)

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("titulo", "categoria", "ativo")
    search_fields = ("titulo", "conteudo", "palavras_chave")
    list_filter = ("ativo", "categoria")
    inlines = [AnexoFAQInline]


# ================================
# 🔹 LIGAÇÃO
# ================================
@admin.register(Ligacao)
class LigacaoAdmin(admin.ModelAdmin):
    list_display = ("id", "chamado", "tipo", "duracao_minutos", "data")
    list_filter = ("tipo",)
    autocomplete_fields = ("chamado",)


# ================================
# 🔹 PESQUISA DE SATISFAÇÃO
# ================================
@admin.register(PesquisaSatisfacao)
class PesquisaSatisfacaoAdmin(admin.ModelAdmin):
    list_display = ("id", "chamado", "nota", "data")
    list_filter = ("nota",)
    autocomplete_fields = ("chamado",)


# ================================
# 🔹 CONTESTAÇÃO
# ================================
@admin.register(ContestacaoChamado)
class ContestacaoChamadoAdmin(admin.ModelAdmin):
    list_display = ("id", "chamado", "data")
    autocomplete_fields = ("chamado",)


# ================================
# 🔹 FECHAMENTO COM AVALIAÇÃO
# ================================
@admin.register(FechamentoAvaliacao)
class FechamentoAvaliacaoAdmin(admin.ModelAdmin):
    list_display = ("id", "chamado", "nota", "data")
    list_filter = ("nota",)
    autocomplete_fields = ("chamado",)


# ================================
# 🔹 FORMULÁRIO DE APROVAÇÃO
# ================================
class CampoFormularioInline(admin.TabularInline):
    model = CampoFormulario
    extra = 0

@admin.register(FormularioAprovacao)
class FormularioAprovacaoAdmin(admin.ModelAdmin):
    list_display = ("nome", "ativo")
    search_fields = ("nome",)
    list_filter = ("ativo",)
    inlines = [CampoFormularioInline]


# ================================
# 🔹 CONFIGURAÇÃO DE ANEXO
# ================================
@admin.register(ConfiguracaoAnexo)
class ConfiguracaoAnexoAdmin(admin.ModelAdmin):
    list_display = ("descricao", "tamanho_max_mb")