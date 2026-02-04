from django.contrib import admin
from .models import Contrato

@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    list_display = ("id", "cliente", "titulo", "data_inicio", "data_fim", "horas_previstas_total", "criado_em")
    search_fields = ("titulo", "descricao", "cliente__nome")
    list_filter = ("cliente", "data_inicio", "data_fim")
