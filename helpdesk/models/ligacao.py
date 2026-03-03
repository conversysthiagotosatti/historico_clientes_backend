from django.db import models


class Ligacao(models.Model):
    """
    Registro de ligação telefônica vinculada a um chamado.
    """
    class TipoLigacao(models.TextChoices):
        ENTRADA = "ENTRADA", "Entrada"
        SAIDA = "SAIDA", "Saída"

    chamado = models.ForeignKey(
        "helpdesk.Chamado", on_delete=models.CASCADE,
        related_name="ligacoes"
    )

    tipo = models.CharField(max_length=10, choices=TipoLigacao.choices,
                            default=TipoLigacao.SAIDA)
    duracao_minutos = models.IntegerField(default=0)
    data = models.DateTimeField(null=True, blank=True)

    telefone_origem = models.CharField(max_length=30, blank=True, null=True)
    telefone_destino = models.CharField(max_length=30, blank=True, null=True)
    observacao = models.TextField(blank=True, null=True)

    codigo_integracao = models.IntegerField(unique=True, null=True, blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Ligação"
        verbose_name_plural = "Ligações"
        ordering = ["-data"]

    def __str__(self):
        return f"Ligação #{self.id} - Chamado #{self.chamado_id}"
