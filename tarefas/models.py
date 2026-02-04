from django.db import models
from contratos.models import Contrato
from django.db.models import Sum

class Tarefa(models.Model):
    class Status(models.TextChoices):
        ABERTA = "ABERTA", "Aberta"
        EM_ANDAMENTO = "EM_ANDAMENTO", "Em andamento"
        CONCLUIDA = "CONCLUIDA", "Concluída"
        CANCELADA = "CANCELADA", "Cancelada"

    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE, related_name="tarefas")
    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, null=True)

    horas_previstas = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ABERTA)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    @property
    def horas_consumidas(self):
        total = self.apontamentos.aggregate(s=Sum("horas"))["s"]
        return total or 0

    def __str__(self):
        return self.titulo


class Apontamento(models.Model):
    tarefa = models.ForeignKey(Tarefa, on_delete=models.CASCADE, related_name="apontamentos")
    data = models.DateField()
    horas = models.DecimalField(max_digits=10, decimal_places=2)
    descricao = models.CharField(max_length=255, blank=True, null=True)

    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tarefa.titulo} - {self.data} - {self.horas}h"

