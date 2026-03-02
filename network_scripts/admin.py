from django.contrib import admin
from .models import (
    Organization,
    Unidade,
    Link,
    ScriptTemplate,
    ScriptGerado
)


# ==========================================
# ORGANIZATION
# ==========================================
@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "ativo", "criado_em")
    search_fields = ("name", "code")
    list_filter = ("ativo",)
    ordering = ("name",)


# ==========================================
# LINK INLINE (DENTRO DA UNIDADE)
# ==========================================
class LinkInline(admin.StackedInline):
    model = Link
    extra = 0
    can_delete = False

    fieldsets = (
        ("🔵 MPLS", {
            "fields": (
                "designacao_mpls",
                "rede_mpls",
                "ip_mpls",
                "ip_mpls_fortigate",
                "mask_mpls",
                "velocidade_mpls",
                "ip_lo_pe_mpls",
            )
        }),
        ("🟢 BLD", {
            "fields": (
                "designacao_bld",
                "ip_bld_pe",
                "ip_bld_fortigate",
                "msk_bld",
                "velocidade_bld",
                "ip_lo_pe_bld",
            )
        }),
        ("🟣 LAN", {
            "fields": (
                "rede_pri_lan",
                "ip_pri_lan_fortigate",
                "mascara_pri_lan",
                "rede_sec_lan",
                "ip_sec_lan_fortigate",
                "mask_sec_lan",
                "vlan_id",
            )
        }),
        ("🟠 Loopbacks", {
            "fields": (
                "loopback_soc",
                "loopback_grc",
                "loopback_cae",
            )
        }),
    )


# ==========================================
# UNIDADE
# ==========================================
@admin.register(Unidade)
class UnidadeAdmin(admin.ModelAdmin):
    list_display = (
        "hostname",
        "organization",
        "cidade",
        "uf",
        "ativo",
        "criado_em",
    )

    search_fields = (
        "hostname",
        "cidade",
        "uf",
    )

    list_filter = (
        "organization",
        "uf",
        "ativo",
    )

    autocomplete_fields = ["organization"]

    inlines = [LinkInline]

    ordering = ("hostname",)


# ==========================================
# SCRIPT TEMPLATE
# ==========================================
@admin.register(ScriptTemplate)
class ScriptTemplateAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "tipo",
        "versao",
        "ativo",
        "criado_em",
    )

    list_filter = (
        "tipo",
        "ativo",
    )

    search_fields = (
        "nome",
        "versao",
    )

    ordering = ("-criado_em",)

    fieldsets = (
        ("📌 Informações Gerais", {
            "fields": (
                "nome",
                "tipo",
                "versao",
                "ativo",
            )
        }),
        ("🧠 Template Jinja2", {
            "fields": ("template",)
        }),
    )


# ==========================================
# SCRIPT GERADO
# ==========================================
@admin.register(ScriptGerado)
class ScriptGeradoAdmin(admin.ModelAdmin):
    list_display = (
        "unidade",
        "template",
        "gerado_por",
        "gerado_em",
        "hash_script",
    )

    search_fields = (
        "unidade__hostname",
        "hash_script",
    )

    list_filter = (
        "template",
        "gerado_em",
    )

    readonly_fields = (
        "script",
        "hash_script",
        "gerado_por",
        "gerado_em",
    )

    ordering = ("-gerado_em",)

    fieldsets = (
        ("📌 Identificação", {
            "fields": (
                "unidade",
                "template",
                "gerado_por",
                "gerado_em",
                "hash_script",
            )
        }),
        ("📜 Script Gerado", {
            "fields": ("script",)
        }),
    )