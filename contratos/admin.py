from django.contrib import admin
from .models import Contrato

@admin.register(Contrato)
class ContratoAdmin(admin.ModelAdmin):
    search_fields = ("titulo", "cliente__nome")
    list_display = ("id", "cliente", "titulo", "data_inicio", "data_fim", "horas_previstas_total")
    list_filter = ("cliente",)
    autocomplete_fields = ("cliente",)
