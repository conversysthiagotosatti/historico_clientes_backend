from django.contrib import admin
from .models import (
    Pais,
    UnidadeFederacao,
    Cidade,
    Cliente
)


# =========================
# PAÍS
# =========================
@admin.register(Pais)
class PaisAdmin(admin.ModelAdmin):
    list_display = ("nome", "abreviatura")
    search_fields = ("nome", "abreviatura")
    ordering = ("nome",)


# =========================
# UNIDADE FEDERAÇÃO (UF)
# =========================
@admin.register(UnidadeFederacao)
class UnidadeFederacaoAdmin(admin.ModelAdmin):
    list_display = ("nome", "sigla", "pais")
    search_fields = ("nome", "sigla", "pais__nome")
    list_filter = ("pais",)
    autocomplete_fields = ("pais",)
    ordering = ("nome",)


# =========================
# CIDADE
# =========================
@admin.register(Cidade)
class CidadeAdmin(admin.ModelAdmin):
    list_display = ("nome", "uf", "codigo_ibge", "codigo_aeroporto")
    search_fields = (
        "nome",
        "uf__nome",
        "uf__sigla",
        "codigo_ibge",
        "codigo_aeroporto",
    )
    list_filter = ("uf",)
    autocomplete_fields = ("uf",)
    ordering = ("nome",)


# =========================
# CLIENTE
# =========================
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "documento",
        "email",
        "telefone",
        "cidade",
        "ativo",
        "criado_em",
    )

    search_fields = (
        "nome",
        "documento",
        "email",
        "telefone",
        "cidade__nome",
        "cidade__uf__sigla",
    )

    list_filter = (
        "ativo",
        "cidade__uf",
    )

    autocomplete_fields = ("cidade",)

    readonly_fields = ("criado_em", "atualizado_em")

    ordering = ("-criado_em",)

    fieldsets = (
        ("Dados Gerais", {
            "fields": (
                "nome",
                "documento",
                "codigo_integracao",
                "ativo",
            )
        }),

        ("Contato", {
            "fields": (
                "email",
                "telefone",
            )
        }),

        ("Endereço", {
            "fields": (
                "cidade",
                "endereco",
                "endereco_numero",
                "endereco_compl",
                "bairro",
                "cep",
            )
        }),

        ("Logotipo", {
            "fields": ("logotipo",)
        }),

        ("Controle", {
            "fields": (
                "criado_em",
                "atualizado_em",
            )
        }),
    )