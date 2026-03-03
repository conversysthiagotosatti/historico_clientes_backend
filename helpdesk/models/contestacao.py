from django.db import models


class ContestacaoChamado(models.Model):
    """
    Contestação de um chamado pelo cliente.
    """
    chamado = models.ForeignKey(
        "helpdesk.Chamado", on_delete=models.CASCADE,
        related_name="contestacoes"
    )
    motivo = models.TextField()
    data = models.DateTimeField(auto_now_add=True)

    codigo_integracao = models.IntegerField(unique=True, null=True, blank=True)

    class Meta:
        verbose_name = "Contestação de Chamado"
        verbose_name_plural = "Contestações de Chamado"
        ordering = ["-data"]

    def __str__(self):
        return f"Contestação #{self.id} - Chamado #{self.chamado_id}"
