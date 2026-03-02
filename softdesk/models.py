from django.db import models


class SoftdeskChamado(models.Model):
    codigo = models.IntegerField(unique=True)
    cliente_codigo = models.CharField(max_length=100, null=True, blank=True)

    cliente = models.ForeignKey(
        "clientes.Cliente",
        on_delete=models.CASCADE,
        related_name="softdesk_chamados",
        null=True,
        blank=True
    )

    status = models.CharField(max_length=100, null=True, blank=True)
    titulo = models.CharField(max_length=255, null=True, blank=True)

    data_abertura = models.DateTimeField(null=True, blank=True)
    data_fechamento = models.DateTimeField(null=True, blank=True)

    raw = models.JSONField()

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Chamado {self.codigo}"