from django.db import models


class AnexoChamado(models.Model):
    """
    Anexo vinculado a um chamado.
    """
    chamado = models.ForeignKey(
        "helpdesk.Chamado", on_delete=models.CASCADE,
        related_name="anexos"
    )
    arquivo = models.FileField(upload_to="helpdesk/anexos_chamado/")
    nome_original = models.CharField(max_length=255, blank=True, null=True)
    tamanho_bytes = models.BigIntegerField(blank=True, null=True)
    mime_type = models.CharField(max_length=120, blank=True, null=True)

    descricao = models.CharField(max_length=255, blank=True, null=True)

    codigo_integracao = models.IntegerField(unique=True, null=True, blank=True)

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Anexo de Chamado"
        verbose_name_plural = "Anexos de Chamado"
        ordering = ["-criado_em"]

    def __str__(self):
        return self.nome_original or f"Anexo {self.id}"
