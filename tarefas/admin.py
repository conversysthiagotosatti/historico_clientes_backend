from django.contrib import admin
from .models import Tarefa, Apontamento

@admin.register(Tarefa)
class TarefaAdmin(admin.ModelAdmin):
    list_display = ("id", "titulo", "contrato", "status", "horas_previstas", "criado_em")
    search_fields = ("titulo", "contrato__titulo", "contrato__cliente__nome")
    list_filter = ("status",)

@admin.register(Apontamento)
class ApontamentoAdmin(admin.ModelAdmin):
    list_display = ("id", "tarefa", "data", "horas")
    list_filter = ("data",)
