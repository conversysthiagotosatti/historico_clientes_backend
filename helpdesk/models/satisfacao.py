from django.db import models


class PesquisaSatisfacao(models.Model):
    """
    Pesquisa de satisfação vinculada a um chamado.
    """
    chamado = models.ForeignKey(
        "helpdesk.Chamado", on_delete=models.CASCADE,
        related_name="pesquisas_satisfacao"
    )
    nota = models.IntegerField(help_text="Nota de 1 a 5")
    comentario = models.TextField(blank=True, null=True)
    data = models.DateTimeField(auto_now_add=True)

    codigo_integracao = models.IntegerField(unique=True, null=True, blank=True)

    class Meta:
        verbose_name = "Pesquisa de Satisfação"
        verbose_name_plural = "Pesquisas de Satisfação"
        ordering = ["-data"]

    def __str__(self):
        return f"Satisfação #{self.id} - Nota {self.nota}"
