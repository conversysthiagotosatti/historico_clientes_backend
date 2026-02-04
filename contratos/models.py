from django.db import models
from clientes.models import Cliente

class Contrato(models.Model):
    cliente = models.ForeignKey("clientes.Cliente", on_delete=models.CASCADE, related_name="contratos",)
    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True, null=True)

    data_inicio = models.DateField()
    data_fim = models.DateField(blank=True, null=True)

    horas_previstas_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.cliente.nome} - {self.titulo}"
