from django.db import models


class FechamentoAvaliacao(models.Model):
    """
    Fechamento com avaliação de chamado.
    """
    chamado = models.ForeignKey(
        "helpdesk.Chamado", on_delete=models.CASCADE,
        related_name="fechamentos_avaliacao"
    )
    nota = models.IntegerField(help_text="Nota de avaliação do fechamento")
    comentario = models.TextField(blank=True, null=True)
    data = models.DateTimeField(auto_now_add=True)

    codigo_integracao = models.IntegerField(unique=True, null=True, blank=True)

    class Meta:
        verbose_name = "Fechamento com Avaliação"
        verbose_name_plural = "Fechamentos com Avaliação"
        ordering = ["-data"]

    def __str__(self):
        return f"Fechamento #{self.id} - Nota {self.nota}"
