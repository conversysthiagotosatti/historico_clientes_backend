from django.contrib import admin
from .models import SoftdeskChamado


@admin.register(SoftdeskChamado)
class SoftdeskChamadoAdmin(admin.ModelAdmin):

    list_display = ("codigo", "status", "cliente_codigo", "atualizado_em")
    search_fields = ("codigo", "cliente_codigo")
    readonly_fields = ("raw",)